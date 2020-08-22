import os
import datetime
import re

from UniversityWebsiteApplication.settings import MEDIA_ROOT
from blog.models import BlogImageUpload
from .BlogTagFactory import (BlogTagFactory, TemplateEnum, URLTag, ImageTag,
							 SectionTag, SubSectionTag, SubSubSectionTag, PTag)
from GenericUtils import tree

__tag_map = {
	"section": TemplateEnum.SECTION,
	"subsection": TemplateEnum.SUB_SECTION,
	"subsubsection": TemplateEnum.SUB_SUB_SECTION,
	"b": TemplateEnum.B,
	"u": TemplateEnum.U,
	"i": TemplateEnum.I,
	"st": TemplateEnum.ST,
	"img": TemplateEnum.IMG,
	"url": TemplateEnum.URL,
	"p": TemplateEnum.P
}


def parse_body(body: str):
	# Nesting of elements not supported (yet)
	""" Get list of all the tags """
	# Create blog tag factory instance
	blog_tag_factory = BlogTagFactory()

	# Get regex match string to search the body for, and create regex object
	regex_str = blog_tag_factory.get_regex_str()
	regex = re.compile(regex_str)

	# Get a list of all matches in the body, and put these into a list formatted ready for the next step
	matches = regex.finditer(body)
	match_positions = []
	# Create a list object ready to store all the custom objects created for each of the tags
	initial_tag_list = []

	# Get a list of all images which need to be moved once the parser has finished (don't want to do this yet as it may
	# except before the HTML fragment is created)
	images_to_move = []

	for match in matches:
		# Set up variables ready to extract values from the current match, giving type hints
		tag_type: str
		val: str

		# Extract values from the match
		tag_type, val = match.group(1), match.group(2)
		# Append the match position to a list ready to collect the normal text later on in the parser
		match_positions.append(match.span())

		# Split string using the ',' character as a delimeter, and then remove any empty space from either side of the
		# values
		parts = list(map(str.strip, str(val).split(",")))

		# Try to create an instance of the required tag
		try:
			tag_to_create = __tag_map.get(tag_type)
		except KeyError:
			# Alert the user that a tag was given that doesn't exist
			# Currently just ignore it
			continue
		else:
			tag = blog_tag_factory.create_blog_tag(tag_to_create, parts[0])
			# print(tag)

		if isinstance(tag, URLTag):
			tag.set_text(parts[1])
		elif isinstance(tag, ImageTag):
			# Construct the path to the temp directory to get the correct image from the tag
			image_path = os.path.join(MEDIA_ROOT, 'temp/{}'.format(tag.get_data()))

			# Get a query set of images, though there should only be one anyways due to the random method of naming
			# the uploaded files
			image_set = BlogImageUpload.objects.filter(image=image_path)

			# If the length of the queryset isn't one, then something's wrong
			if len(image_set) is not 1:
				# Could implement a feature in the future where broken references like this can be fixed after the
				# initial upload
				continue

			# Get the first (and only) image from the queryset
			required_image = image_set[0]
			print(required_image)

			# Get the new image path for the image
			new_path = get_new_image_path(image_path)
			images_to_move.append((image_path, new_path))

			# Set the new URL data and alt information on the tag
			tag.set_data(new_path)
			tag.set_alt(required_image.alt_text)

			initial_tag_list.append(tag)

	# Now, the text between the tags needs to be added to tags too, ready for creating the tree
	complete_tag_list = []
	# Get a reference to the first element ready to iterate through the list of match positions
	previous_pos = match_positions[0]

	# If the first match isn't at the start of the string, then create a PTag object to hold the text up to this point
	if previous_pos[0] != 0:
		# Get the text before the first tag, and split this into the required <p> tags
		start_text = body[:previous_pos[0] - 1]
		start_p_tags = split_string_to_p_tags(start_text, blog_tag_factory)
		complete_tag_list.extend(start_p_tags)

	# Iterate through the remaining tags, collecting the text in-between as matching
	for index, position in enumerate(match_positions[1:]):
		# Add previous tag to the complete list
		complete_tag_list.append(initial_tag_list[index])

		# Extract the start and end match position from the position tuple
		start, end = position

		# Extract the start and end match position from the previous position tuple
		prev_start, prev_end = previous_pos

		# If the current start position and previous end position are different, then there's other text between this
		# tag and the previous tag which needs to be collected
		if not(start == prev_end):
			# The values are passed with this way as the regex matches give the absolute start of the pattern, but the
			# end match position is one after the actual end of the pattern
			between_text = body[prev_end:start-1]
			# Split the text into paragraphs (if any at all)
			p_tags = split_string_to_p_tags(between_text, blog_tag_factory)
			# Add the new tag(s) to the complete tag list
			complete_tag_list.extend(p_tags)

		# Set the previous position to the current position ready for the next loop
		previous_pos = position

	complete_tag_list.append(initial_tag_list[-1])

	""" Sort these into a tree structure """
	new_tree = __tag_list_to_tree(complete_tag_list)

	""" Format the tree into a HTML string """
	html_string = tree_to_html_string(new_tree)
	print(html_string)

	"""" Return the formatted HTML for the token tree """
	return html_string


def split_string_to_p_tags(to_split: str, factory: BlogTagFactory):
	p_tags = []

	paragraphs = to_split.split("\n\n")
	print(paragraphs)

	for paragraph in paragraphs:
		if not(len(paragraph) > 0) or paragraph.isspace():
			continue

		p_tags.append(factory.create_blog_tag(TemplateEnum.P, paragraph))

	return p_tags


def get_new_image_path(old_path):
	# Get the current date ready to construct the required image path
	date = datetime.date.today()

	# Format the path to create with the MEDIA_ROOT, current year, current date, and filename
	filename = old_path.split("/")[-1]
	new_image_path = r'{}/blog/{}/{}/{}'.format(MEDIA_ROOT, date.year, date.month, filename)

	return new_image_path


def move_image_to_static_location(to_move: tuple):
	# Split the tuple into the required values
	new_path, old_path = to_move

	# Get the directory structure to create ready to try and create it
	new_image_directory = "/".join(str.split(new_path)[0:-1])

	try:
		# Attempt to create the new directory
		os.makedirs(new_image_directory)
	except OSError as ose:
		# Creating the directory structure, set up log system to report the exact error with this at a later point
		return False
	else:
		# Move the image to the newly created directory
		new_image_path = new_image_directory + old_path.split("/")[-1]
		os.rename(old_path, new_image_path)

	return True


__nest_sensitive_elements = (SectionTag, SubSectionTag, SubSubSectionTag)


def tree_to_html_string(node: tree.Tree):
	current_strings = []
	val: tree.Tree
	for val in node.get_children():
		if isinstance(val.data, __nest_sensitive_elements):
			current_strings.append(tree_to_html_string(val))
		else:
			current_strings.append(val.data.convert_to_html())

	return str.join(current_strings)


def __tag_list_to_tree(tag_list: list):
	# Construct tree root node
	root_node = tree.Tree(data=None)
	# Get a reference to the current node (for the sake of adding new tree objects to the correct node)
	current_node = root_node
	# Create a nest index counter ready for use in the iteration, this will be used to gauge where new tree objects
	# should be added
	current_nest_index = 0

	for tag in tag_list:
		# Create a new tree node with the tag as the data
		new_node = tree.Tree(data=tag)
		if isinstance(tag, __nest_sensitive_elements):
			# Get the nest index of the current tag (where the index defines the order of nesting)
			nest_index = __nest_sensitive_elements.index(tag.__class__)

			# Nesting must only increase by one at a given time, but can decrease an unbounded amount
			if current_nest_index - nest_index > 1:
				# Nesting is incorrect, as in it skipped a nesting step
				return None

			# Nesting is correct, continue
			if nest_index < current_nest_index:
				# If the nest index is less than the current nest index, then we need to go up two tree layers to add
				# the tag to the correct section layer
				prev_node = tree.find_parent_of_node(root_node, current_node)
				prev_prev_node = tree.find_parent_of_node(root_node, prev_node)
				prev_prev_node.insert_node(new_node)
			elif nest_index == current_nest_index:
				# If the nest index is the same as the current nest index, then we need to go up one tree layer instead
				# to add the tag to the correct section layer
				prev_node = tree.find_parent_of_node(root_node, current_node)
				prev_node.insert_node(new_node)
			else:
				# The nest index is greater than the current next index, meaning the section is one lower than the
				# current one. Therefore, we add the newly created node
				current_node.insert_node(new_node)

			# Set the current node to the newly added node
			current_node = new_node

			# Set the current next index to the new one
			current_nest_index = nest_index

		else:
			# The tag isn't a section tag, and is therefore not sensitive to nesting, so just add it to the current node
			current_node.insert_node(new_node)

	return root_node

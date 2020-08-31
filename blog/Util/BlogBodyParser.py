import os
import re

from UniversityWebsiteApplication.settings import MEDIA_ROOT
from blog.models import BlogImageUpload, BlogImageToMove, Post
from .Exceptions import report_exception
from .BlogTagFactory import (BlogTagFactory, TemplateEnum, URLTag, ImageTag,
							 SectionTag, SubSectionTag, SubSubSectionTag, PTag)
from GenericUtils import media_utils
from GenericUtils.tree import Tree, find_parent_of_node

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
	"p": TemplateEnum.P,
	"none": TemplateEnum.NONE
}


def parse_body(body: str, post: Post):
	""" Split input body into paragraphs around the \n tag """
	paragraphs = [s for s in body.replace("\r", "\n").split("\n") if s.strip() != '']

	""" Get list of all the tags """
	# Create blog tag factory instance
	blog_tag_factory = BlogTagFactory()

	# Get regex match string to search the body for, and create regex object
	regex_str = blog_tag_factory.get_regex_str()
	regex = re.compile(regex_str)

	tag_tree_root = Tree(data=None)
	current_node = tag_tree_root
	current_nest_index = -1

	for paragraph in paragraphs:
		# Get the index of the end of the paragraph
		paragraph_end = len(paragraph) - 1
		# Get a iterator of all the regex matches
		matches = regex.finditer(paragraph)
		# Attempt to get the first match in the matches
		first_match = next(matches, None)

		# If there isn't a match, then there are no tags in this paragraph, can just construct a p tag for the text
		if first_match is None:
			first_tag = __create_tag("p", paragraph, blog_tag_factory)
			current_node, current_nest_index = __add_tag_to_tree(tag_tree_root, current_node, first_tag,
																 current_nest_index, post)
			# Begin next loop
			continue

		# Get the start and end positions of the tag, as well as the tag type (first regex match) and the value of the
		# tag (second regex match)
		start, end = first_match.span()
		tag_type, val = first_match.group(1), first_match.group(2)

		# If the end of the match (adjusted so that it is the actual end of the match, as the regex grabs one extra
		# character) minus the start of the match is equal to the end index of the paragraph, then the match takes up
		# the entire paragraph, so no need to worry about sorting out the text into individual parts
		if (end - 1) - start == paragraph_end:
			# Create a tag object
			first_tag = __create_tag(tag_type, val, blog_tag_factory)

			if not isinstance(first_tag, __nest_sensitive_elements):
				wrapper = __create_wrapper_p_tag(blog_tag_factory)
				wrapper.insert_node(first_tag)
				first_tag = wrapper

			# Add this tag object to the tree
			current_node, current_nest_index = __add_tag_to_tree(tag_tree_root, current_node, first_tag,
																 current_nest_index, post)
			# Begin next loop
			continue

		empty_p_tag = blog_tag_factory.create_blog_tag(TemplateEnum.P, None)
		wrapper = Tree(data=empty_p_tag)

		# If the match doesn't start at the first index of the paragraph, then there is text before the first tag
		if start != 0:
			text_before = paragraph[0:start]
			first_tag = __create_tag("none", text_before, blog_tag_factory)
			wrapper.insert_node(first_tag)

		# Add first tag to the wrapper also
		first_match_tag = __create_tag(tag_type, val, blog_tag_factory)
		wrapper.insert_node(first_match_tag)

		# Iterate through the remaining tags to add (if any)
		prev_start, prev_end = start, end
		for match in matches:
			tag_type, val = match.group(0), match.group(1)
			start, end = match.span()
			if prev_end != start:
				# There's text between this tag and the previous tag, so capture this into it's own node
				between_text = paragraph[prev_end:start - 1]
				new_tag = __create_tag("none", between_text, blog_tag_factory)
				wrapper.insert_node(new_tag)

			# Add the matched tag itself
			matched_tag = __create_tag(tag_type, val, blog_tag_factory)
			wrapper.insert_node(matched_tag)

			# Set the vals for prev_start and prev_end to the current values
			prev_start, prev_end = start, end

		# Now, check if there was any text after the final matched tag
		if prev_end != paragraph_end:
			final_text = paragraph[prev_end:paragraph_end]
			final_text_tag = __create_tag("none", final_text, blog_tag_factory)
			wrapper.insert_node(final_text_tag)

		# All text and tags have now been added, so we can now add the wrapper tag to the tree
		current_node, current_nest_index = __add_tag_to_tree(tag_tree_root, current_node, wrapper, current_nest_index,
															 post)

	return __tree_to_html_string(tag_tree_root, 0)


def __create_wrapper_p_tag(btf: BlogTagFactory, data: str = None):
	# Create the empty p tag as a wrapper for all the elements inside of a text
	empty_p_tag = btf.create_blog_tag(TemplateEnum.P, None)
	# Create the tree object ready to return
	return_tree = Tree(data=empty_p_tag)
	if data is not None:
		# If the data isn't None, then create a NoneTag object to hold the passed text and add this as a child of the
		# wrapper tag
		child = __create_tag("none", data, btf)
		return_tree.insert_node(child)

	return return_tree


def __create_tag(tag_type: str, val: str, btf: BlogTagFactory):
	# Try to create an instance of the required tag
	try:
		tag_to_create = __tag_map.get(tag_type)
	except KeyError:
		# Put an entry into the exception database for debugging
		report_exception()
		return None
	else:
		tag = btf.create_blog_tag(tag_to_create, val)

		if isinstance(tag, URLTag):
			values = [vals.strip() for vals in val.split(",")]
			tag.data = values[0]
			tag.text = values[1]

	return tag


def __add_tag_to_tree(root_node: Tree, current_node: Tree, tag, current_nest_index, post: Post):
	if isinstance(tag, Tree):
		new_node = tag
	else:
		new_node = Tree(data=tag)

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
			prev_node = find_parent_of_node(root_node, current_node)
			prev_prev_node = find_parent_of_node(root_node, prev_node)
			prev_prev_node.insert_node(new_node)
		elif nest_index == current_nest_index:
			# If the nest index is the same as the current nest index, then we need to go up one tree layer instead
			# to add the tag to the correct section layer
			prev_node = find_parent_of_node(root_node, current_node)
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
		# Iterate through the tag's children to check for any image tags, and then deal with them
		if isinstance(tag, Tree):
			for child in tag.children:
				if isinstance(child.data, ImageTag):
					new_path, alt_text = __deal_with_image(child.data.data, post)
					child.data.data = new_path
					child.data.alt = alt_text
		# The tag isn't a section tag, or an image tag, and therefore does not require special processing, so just add
		# it to the current node
		current_node.insert_node(new_node)

	return current_node, current_nest_index


# region Image Based Methods
def __deal_with_image(tag_data: str, post: Post):
	# Construct the path to the temp directory to get the correct image from the tag
	image_path = os.path.join(MEDIA_ROOT, f'temp/{tag_data}')

	# Get a query set of images, though there should only be one anyways due to the random method of naming
	# the uploaded files
	image_set = BlogImageUpload.objects.filter(image=image_path)

	# If the length of the queryset isn't one, then something's wrong
	if len(image_set) != 1:
		# Could implement a feature in the future where broken references like this can be fixed after the
		# initial upload
		return None

	# Get the first (and only) image from the queryset
	required_image = image_set[0]

	# Get the new image path for the image
	new_path = media_utils.get_new_path_in_media_root(image_path)

	# Create the database object to hold the old and new path ready to move it once the parsing of the body has finished
	image_to_upload = BlogImageToMove()
	image_to_upload.temp_path = image_path
	image_to_upload.new_path = new_path
	image_to_upload.post_id = post
	image_to_upload.save()

	# The image tag itself doesn't need the absolute path to the image, instead give the url from media
	image_path_to_return = "/" + "/".join(new_path.split("/")[-5:])

	return image_path_to_return, required_image.alt_text
# endregion


# region Tree Based Methods
__nest_sensitive_elements = (SectionTag, SubSectionTag, SubSubSectionTag)


def __tree_to_html_string(node: Tree, tab_index: int):
	current_strings = []
	child: Tree
	for child in node.children:
		if isinstance(child.data, __nest_sensitive_elements):
			# Set the recursive call of this object's children as it's data, needed to format the HTML correctly
			child.data.data = __tree_to_html_string(child, tab_index + 1)
		elif isinstance(child.data, PTag):
			if len(child.children) > 0:
				child_string = [val.data.convert_to_html() for val in child.children]
				child.data.data = "".join(child_string)

		current_strings.append(child.data.convert_to_html())

	return_val = ("\n" + "\t" * tab_index).join(current_strings)
	if tab_index > 0:
		return ("\t" * tab_index) + return_val

	return return_val
# endregion

import enum
from .Exceptions import BlogTagMethodNotImplementedException, report_exception


class TemplateEnum(enum.Enum):
	SECTION = 1
	SUB_SECTION = 2
	SUB_SUB_SECTION = 3
	B = 4
	U = 5
	I = 6
	ST = 7
	IMG = 8
	URL = 9
	P = 10
	NONE = 11


# region Class Definitions
class __BlogTagBase:
	def __init__(self, data):
		if data is None:
			self.data = ''
		else:
			self.data = data

	def regex_check_format(self):
		raise BlogTagMethodNotImplementedException

	def convert_to_html(self):
		raise BlogTagMethodNotImplementedException

	def __str__(self):
		return f"Type: {self.__class__}, Data: {self.data}"


class SectionTag(__BlogTagBase):
	def __init__(self, data, title):
		super().__init__(data)
		self.data = data
		self.title = title

	def get_title(self):
		return self.title

	def regex_check_format(self):
		return 'section|SECTION'

	def convert_to_html(self):
		return f'<div class="section">\n\t<h2>{self.title}</h2>\n{self.data}\n</div>'

	def __str__(self):
		return f"{super().__str__()}\nTitle: {self.title}"


class SubSectionTag(SectionTag):

	def regex_check_format(self):
		return 'subsection|SUBSECTION'

	def convert_to_html(self):
		return f'<div class="subsection">\n\t\t<h3>{self.title}</h3>\n{self.data}\n\t</div>'


class SubSubSectionTag(SectionTag):

	def regex_check_format(self):
		return 'subsubsection|SUBSUBSECTION'

	def convert_to_html(self):
		return f'<div class="subsubsection">\n\t\t\t<h4>{self.title}</h4>\n{self.data}\n\t\t</div>'


class BoldTag(__BlogTagBase):

	def regex_check_format(self):
		return '[bB]'

	def convert_to_html(self):
		return f'<strong class="text-weight-bold">{self.data}</strong>'


class ItalicTag(__BlogTagBase):

	def regex_check_format(self):
		return '[iI]'

	def convert_to_html(self):
		return f'<emp class="text-weight-italic">{self.data}</emp>'


class UnderlineTag(__BlogTagBase):

	def regex_check_format(self):
		return '[uU]'

	def convert_to_html(self):
		return f'<ins>{self.data}</ins>'


class StruckThroughTag(__BlogTagBase):

	def regex_check_format(self):
		return 'st|ST'

	def convert_to_html(self):
		return f'<del>{self.data}</del>'


class ImageTag(__BlogTagBase):
	alt = ''

	def regex_check_format(self):
		return 'img|IMG'

	def convert_to_html(self):
		return f'<img src="{self.data}" alt="{self.alt}"/>'

	def __str__(self):
		return f"{super().__str__()}\nAlt: {self.alt}"


class URLTag(__BlogTagBase):
	text = ''

	def regex_check_format(self):
		return 'url|URL'

	def convert_to_html(self):
		return f'<a href="{self.data}">{self.text}</a>'

	def __str__(self):
		return f"{super().__str__()}\nText: {self.text}"


class PTag(__BlogTagBase):

	def regex_check_format(self):
		# The user should not be able to create an instance of this tag, so return anm empty string
		return ''

	def convert_to_html(self):
		return f'<p>{self.data}</p>'


class NoneTag(__BlogTagBase):
	def regex_check_format(self):
		# We don't need to check for this tag, it is purely to contain raw text data
		return ''

	def convert_to_html(self):
		# There is no specific tag to convert the data into, as this is just a container of data, so just return the
		# data this tag holds
		return self.data
# endregion


# region Generator methods
def _section_tag_generator(title):
	tag = SectionTag(None, title)
	return tag


def _sub_section_tag_generator(title):
	tag = SubSectionTag(None, title)
	return tag


def _sub_sub_section_tag_generator(title):
	tag = SubSubSectionTag(None, title)
	return tag


def _bold_tag_generator(data):
	tag = BoldTag(data)
	return tag


def _italic_tag_generator(data):
	tag = ItalicTag(data)
	return tag


def _underline_tag_generator(data):
	tag = UnderlineTag(data)
	return tag


def _struckthrough_tag_generator(data):
	tag = StruckThroughTag(data)
	return tag


def _image_tag_generator(data):
	tag = ImageTag(data)
	return tag


def _url_tag_generator(data):
	tag = URLTag(data)
	return tag


def _p_tag_generator(data):
	tag = PTag(data)
	return tag


def _none_tag_generator(data):
	tag = NoneTag(data)
	return tag
# endregion


class BlogTagFactory:
	__tag_list = {
		SectionTag,
		SubSectionTag,
		SubSubSectionTag,
		BoldTag,
		ItalicTag,
		UnderlineTag,
		StruckThroughTag,
		ImageTag,
		URLTag,
		PTag,
		NoneTag
	}

	def __init__(self):
		self.__regex_str = r'\\({})'.format(self.__collect_tag_regex()) + r'\{(.*?)\}'

	def create_blog_tag(self, tag: TemplateEnum, data):
		try:
			function = self.function_dict.get(tag)
		except KeyError:
			# Add error to database to allow for easier debugging of errors
			report_exception()
		else:
			return function(str(data))

	function_dict = {
		TemplateEnum.SECTION: _section_tag_generator,
		TemplateEnum.SUB_SECTION: _sub_section_tag_generator,
		TemplateEnum.SUB_SUB_SECTION: _sub_sub_section_tag_generator,
		TemplateEnum.B: _bold_tag_generator,
		TemplateEnum.I: _italic_tag_generator,
		TemplateEnum.U: _underline_tag_generator,
		TemplateEnum.ST: _struckthrough_tag_generator,
		TemplateEnum.IMG: _image_tag_generator,
		TemplateEnum.URL: _url_tag_generator,
		TemplateEnum.P: _p_tag_generator,
		TemplateEnum.NONE: _none_tag_generator
	}

	def get_regex_str(self):
		return self.__regex_str

	def __collect_tag_regex(self):
		return '|'.join(str(c.regex_check_format(c)) for c in self.__tag_list)

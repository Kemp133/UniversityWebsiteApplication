import sys
import enum
from .Exceptions import BlogTagMethodNotImplementedException
from blog.models import BlogExceptions


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


# region Class Definitions
class __BlogTagBase:
	def __init__(self, data):
		if data is None:
			self._data = ''
		else:
			self._data = data

	def get_data(self):
		return self._data

	def regex_check_format(self):
		raise BlogTagMethodNotImplementedException

	def convert_to_html(self):
		raise BlogTagMethodNotImplementedException

	def __str__(self):
		return f"Data: {self._data}"


class SectionTag(__BlogTagBase):
	def __init__(self, data, title):
		super().__init__(data)
		self._data = data
		self._title = title

	def set_data(self, data):
		self._data = data

	def get_title(self):
		return self._title

	def regex_check_format(self):
		return 'section|SECTION'

	def convert_to_html(self):
		return '<div class="section">\n<h1>{}</h1>\n{}\n</div>'.format(self._title, self._data)

	def __str__(self):
		return f"{super().__str__()}\nTitle: {self._title}"


class SubSectionTag(SectionTag):

	def regex_check_format(self):
		return 'subsection|SUBSECTION'

	def convert_to_html(self):
		return '<div class="subsection">\n<h3>{}</h3>\n{}\n</div>'.format(self._title, self._data)


class SubSubSectionTag(SectionTag):

	def regex_check_format(self):
		return 'subsubsection|SUBSUBSECTION'

	def convert_to_html(self):
		return '<div class="subsubsection">\n<h5>{}</h5>\n{}\n</div>'.format(self._title, self._data)


class BoldTag(__BlogTagBase):

	def regex_check_format(self):
		return '[bB]'

	def convert_to_html(self):
		return '<strong>{}</strong>'.format(self._data)


class ItalicTag(__BlogTagBase):

	def regex_check_format(self):
		return '[iI]'

	def convert_to_html(self):
		return '<emp>{}</emp>'.format(self._data)


class UnderlineTag(__BlogTagBase):

	def regex_check_format(self):
		return '[uU]'

	def convert_to_html(self):
		return '<ins>{}</ins>'.format(self._data)


class StruckThroughTag(__BlogTagBase):

	def regex_check_format(self):
		return 'st|ST'

	def convert_to_html(self):
		return '<del>{}</del>'.format(self._data)


class ImageTag(__BlogTagBase):
	_alt = ''

	def set_data(self, data):
		self._data = data

	def set_alt(self, alt):
		self._alt = alt

	def regex_check_format(self):
		return 'img|IMG'

	def convert_to_html(self):
		return '<img src={} alt={} />'.format(self._data, self._alt)

	def __str__(self):
		return f"{super().__str__()}\nAlt: {self._alt}"


class URLTag(__BlogTagBase):
	_text = ''

	def set_text(self, text):
		self._text = text

	def get_text(self):
		return self._text

	def regex_check_format(self):
		return 'url|URL'

	def convert_to_html(self):
		return '<a href={}>{}</a>'.format(self._data, self._text)

	def __str__(self):
		return f"{super().__str__()}\nText: {self._text}"


class PTag(__BlogTagBase):
	def regex_check_format(self):
		return ''

	def convert_to_html(self):
		return '<p>{}</p>'.format(self._data)
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
		PTag
	}

	def __init__(self):
		self.__regex_str = r'\\({})'.format(self.__collect_tag_regex()) + r'\{(.*?)\}'

	def create_blog_tag(self, tag: TemplateEnum, data):
		try:
			function = self.function_dict.get(tag)
		except KeyError as ke:
			# Add error to database to allow for easier debugging of errors
			exc_type, value, traceback = sys.exc_info()
			new_exception = BlogExceptions()
			new_exception.exc_type = exc_type
			new_exception.value = value
			new_exception.traceback = traceback
			new_exception.save()
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
		TemplateEnum.P: _p_tag_generator
	}

	def get_regex_str(self):
		return self.__regex_str

	def __collect_tag_regex(self):
		return '|'.join(str(c.regex_check_format(c)) for c in self.__tag_list)

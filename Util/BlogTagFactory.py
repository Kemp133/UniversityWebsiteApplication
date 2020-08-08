import enum


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


class BlogTagFactory:
    __TAG_START, __CONTENT_START, __CONTENT_END = '\\', '{', '}'

    def section_tag_generator(self):
        pass

    function_dict = {
        TemplateEnum.SECTION: section_tag_generator,

    }

    def get_formatted_tag(self, template_type: TemplateEnum, **kwargs):
        pass


class __BlogTagBase:
    _data = ''

    def set_value(self, data):
        self._data = data

    def set_title(self, title):
        self._title = title

    def regex_check_format(self):
        raise BlogTagIsNotImplementedException


class ImageTag(__BlogTagBase):
    _alt = ''

    def set_alt(self, alt):
        self._alt = alt

    def regex_check_format(self):
        return '(img|IMG)'


class BlogTagIsNotImplementedException(Exception):
    # This should be set in the base class, so that any unimplemented methods can be detected quickly
    pass

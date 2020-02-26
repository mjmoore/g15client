Adapted from [Dan Bader](https://dbader.org/blog/monochrome-font-rendering-with-freetype-and-python).
Minor changes made to work with python 3.x. 

#### Usage
    >>> from font import Font
    >>> fnt = Font("helvetica.ttf", 24)
    >>> txt = fnt.render_text("hello")
    >>> repr(txt)
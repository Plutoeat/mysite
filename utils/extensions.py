#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/6 17:37
# @Author  : Joker
# @File    : extensions.py
# @Software: PyCharm
import re
import xml.etree.ElementTree as etree
from xml.etree.ElementTree import Element

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.extensions.footnotes import FootnoteExtension, FN_BACKLINK_TEXT, NBSP_PLACEHOLDER
from markdown.extensions.toc import TocTreeprocessor, TocExtension
from markdown.inlinepatterns import InlineProcessor
from markdown.treeprocessors import Treeprocessor


class TocProcessor(TocTreeprocessor):
    def build_toc_div(self, toc_list: list) -> etree.Element:
        """ Return a string div given a toc list. """
        div = etree.Element("div")
        div.attrib["class"] = self.toc_class

        # Add title to the div
        if self.title:
            header = etree.SubElement(div, "span")
            if self.title_class:
                header.attrib["class"] = self.title_class
            header.text = self.title

        def build_etree_ul(toc_list: list, parent: etree.Element) -> etree.Element:
            ul = etree.SubElement(parent, "ul")
            # 添加自己的样式
            if parent.attrib['class'] == 'toc':
                ul.attrib['class'] = "text-sm shadow-sm p-2 border bg-transparent rounded"
            else:
                ul.attrib["class"] = "text-sm"
            for item in toc_list:
                # List item link, to be inserted into the toc div
                li = etree.SubElement(ul, "li")
                link = etree.SubElement(li, "a")
                link.text = item.get('name', '')
                link.attrib["href"] = '#' + item.get('id', '')
                # 添加自己的样式属性给目录
                li.attrib["class"] = "ps-2"
                link.attrib['class'] = "text-gray-700 dark:text-gray-300 decoration-2 font-medium hover:underline hover:text-indigo-600 dark:hover:text-indigo-500"
                if item['children']:
                    build_etree_ul(item['children'], li)
            return ul

        build_etree_ul(toc_list, div)

        if 'prettify' in self.md.treeprocessors:
            self.md.treeprocessors['prettify'].run(div)

        return div


class CustomTocExtension(TocExtension):
    TreeProcessorClass = TocProcessor
    """
    自定义目录拓展
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class CommonProcessor(Treeprocessor):
    """遍历根节点并修改任何发现的标签"""

    classes = {
        "h1": "scroll-m-20 text-4xl mt-8 mb-4 font-extrabold tracking-tight dark:text-neutral-200",
        "h2": "scroll-m-20 border-b pb-2 text-3xl mt-6 mb-3 font-semibold tracking-tight first:mt-0 dark:text-neutral-200",
        "h3": "scroll-m-20 text-2xl mt-5 mb-2 font-medium tracking-tight dark:text-neutral-200",
        "h4": "scroll-m-20 text-xl mt-4 mb-2 font-medium tracking-tight dark:text-neutral-200",
        "h5": "scroll-m-20 text-lg mt-3 mb-1 font-normal tracking-tight dark:text-neutral-200",
        "h6": "scroll-m-20 text-base mt-2 mb-1 font-light tracking-tight dark:text-neutral-200",
        "p": "leading-normal [&:not(:first-child)]:mt-6 text-base font-normal text-black dark:text-neutral-200",
        "blockquote": "mt-6 border-l-2 pl-6",
        "code": "relative rounded bg-muted px-[0.3rem] py-[0.2rem] text-sm font-semibold dark:text-neutral-200",
        "a": "text-primary decoration-2 font-medium hover:underline"
    }

    def run(self, root):
        for node in root.iter():
            tag_classes = self.classes.get(node.tag)
            if tag_classes:
                if node.get('class'):
                    node.attrib["class"] = node.attrib['class'] + " " + tag_classes
                else:
                    node.attrib['class'] = tag_classes


class CommonExtension(Extension):
    """一个用于向标签添加类的扩展"""

    def extendMarkdown(self, md):
        md.treeprocessors.register(
            CommonProcessor(md), "common", 20)


class ListProcessor(Treeprocessor):
    def run(self, root):
        # Iterate through all elements
        for element in root.iter():
            if element.tag == 'ul':
                element.attrib['class'] = "my-6 ml-6 list-disc list-outside [&>li]:mt-2 dark:text-neutral-200"
                # Check if this is a task list
                self.process_unordered_list(element)
            elif element.tag == 'ol':
                element.attrib['class'] = "my-6 ml-6 list-decimal list-outside [&>li]:mt-2 dark:text-neutral-200"
                self.process_ordered_list(element)

    def process_unordered_list(self, ul):
        for li in ul.findall('li'):
            # Check for task list item
            if li.text and li.text.strip().startswith('[ ]'):
                ul.attrib['style'] = "padding-inline-start: 0px;"
                ul.attrib['class'] = "my-6 list-disc list-outside [&>li]:mt-2 dark:text-neutral-200"
                li.attrib['style'] = "list-style-type: none;"
                self.create_task_list_item(li, 'unchecked')
            elif li.text and li.text.strip().startswith('[x]'):
                ul.attrib['style'] = "padding-inline-start: 0px;"
                ul.attrib['class'] = "my-6 list-disc list-outside [&>li]:mt-2 dark:text-neutral-200"
                li.attrib['style'] = "list-style-type: none;"
                self.create_task_list_item(li, 'checked')

    def create_task_list_item(self, li, status):
        # Create a checkbox for task list items
        checkbox = Element('input', type='checkbox', disabled='true')
        if status == 'checked':
            checkbox.set('checked', 'checked')
        li.insert(0, checkbox)
        label = Element('label')
        label.set('class', 'pl-2')
        # Remove the [ ] or [x] from the text
        label.text = li.text[3:]
        li.insert(1, label)
        li.text = ""

    def process_ordered_list(self, ol):
        for li in ol.findall('li'):
            text = li.text
            li.text = ''
            span = etree.SubElement(li, 'span')
            span.text = text
            span.set('class', 'mt-0 pl-2 text-sm text-gray-800 dark:text-neutral-200')


class ListExtension(Extension):
    """
    列表渲染拓展
    """
    def extendMarkdown(self, md):
        md.treeprocessors.register(ListProcessor(md), 'list', 5)


class DelInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element('del')
        el.text = m.group(1)
        return el, m.start(0), m.end(0)


class DelExtension(Extension):
    """
    渲染删除线
    """
    def extendMarkdown(self, md):
        DEL_PATTERN = r'~~(.*?)~~'  # like --del--
        md.inlinePatterns.register(DelInlineProcessor(DEL_PATTERN, md), 'del', 10)


class HighlightInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element('span')
        el.text = m.group(1)
        el.set('class', 'text-base px-2 py-2 mx-2 rounded-md leading-6 text-neutral-200 bg-indigo-800/70 dark:bg-indigo-200/70 dark:text-gray-800')
        return el, m.start(0), m.end(0)


class HighlightExtension(Extension):
    """
    渲染高亮
    """
    def extendMarkdown(self, md):
        HIGH_LIGHT_PATTERN = r'==(.*?)=='  # like --del--
        md.inlinePatterns.register(HighlightInlineProcessor(HIGH_LIGHT_PATTERN, md), 'highlight', 15)


class FoldProcessor(Treeprocessor):
    def run(self, root):
        for child in root.iter('p'):
            if child.text and child.text.startswith('details:'):
                text_list = child.text.split('\n')
                details = etree.Element('details', {'class': 'group border-b'})
                summary = etree.Element('summary', {'class': 'px-4 py-2 cursor-pointer text-lg font-medium text-gray-800 bg-gray-100 group-open:bg-gray-200'})
                div = etree.Element('div', {'class': 'px-4 py-2'})
                summary.text = text_list[0].strip('details:').strip()
                for p_text in text_list[1:]:
                    p = etree.Element('p', {'class': 'leading-normal [&:not(:first-child)]:mt-6 text-base font-normal text-black dark:text-neutral-200'})
                    p.text = p_text
                    div.append(p)
                details.append(summary)
                details.append(div)
                p_index = list(root).index(child)
                root.remove(child)
                root.insert(p_index, details)


class FoldExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(FoldProcessor(md), "fold", 20)


class ImageProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        figure = etree.Element('figure')
        img = etree.SubElement(figure, 'img', {
            'class': 'w-full object-cover rounded-xl',
            'src': m.group(2),
            'alt': m.group(1)
        })
        title = etree.Element('div')
        title.attrib['class'] = "scroll-m-20 text-2xl mt-5 mb-2 font-medium tracking-tight dark:text-neutral-200"
        title.attrib['style'] = "text-align: center"
        title.text = m.group(3)
        figcaption = etree.Element('figcaption')
        figcaption.attrib['class'] = 'mt-3 text-sm text-center text-gray-500 dark:text-neutral-500'
        figcaption.text = m.group(1)
        figure.insert(0, title)
        figure.insert(2, figcaption)
        return figure, m.start(0), m.end(0)


class ImageExtension(Extension):
    """
    图片处理拓展
    """
    def extendMarkdown(self, md):
        IMAGE_PATTERN = r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]+)")?\)'
        md.inlinePatterns.register(ImageProcessor(IMAGE_PATTERN, md), "custom-image", 175)


class IconInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        text = m.group(1)
        el = etree.Element('i')
        el.set('class', 'fa fa-{}'.format(text.replace('icon:', '')))
        return el, m.start(0), m.end(0)


class IconExtension(Extension):
    """
    渲染图标
    匹配：icon:exclamation-triangle
    输出：<i class="fa fa-exclamation-triangle"></i>
    """

    def extendMarkdown(self, md):
        ICON_PATTERN = r'(icon:[a-z-]+)'
        md.inlinePatterns.register(IconInlineProcessor(ICON_PATTERN, md), 'icon', 180)


class TableProcessor(Treeprocessor):
    def run(self, root):
        for table in root.iter('table'):
            trs = table.iter('tr')
            for tr in trs:
                tr.attrib['class'] = "m-0 border-t p-0 even:bg-muted"
            tds = table.iter('td')
            for td in tds:
                td.attrib[
                    'class'] = "border px-4 py-2 text-left [&[align=center]]:text-center [&[align=right]]:text-right dark:text-neutral-200"
            ths = table.iter('th')
            for th in ths:
                th.attrib[
                    'class'] = "border px-4 py-2 text-left font-bold [&[align=center]]:text-center [&[align=right]]:text-right dark:text-neutral-200"
            table.attrib['class'] = "w-full"
            # 创建一个div元素并设置类名
            div = Element('div')
            div.attrib['class'] = "my-6 w-full overflow-y-auto"
            # 将table元素包裹在div中
            el_index = list(root).index(table)
            root.remove(table)
            div.append(table)
            root.insert(el_index, div)


class TableExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(TableProcessor(md), "table", 185)


class AlertBlockProcessor(BlockProcessor):
    RE_FENCE_START = r'^:{3}\s*primary\s*.*\n*|^:{3}\s*secondary\s*.*\n*|^:{3}\s*success\s*.*\n*|^:{3}\s*error\s*.*\n*|^:{3}\s*warning\s*.*\n*|^:{3}\s*info\s*.*\n*'
    RE_FENCE_END = r'\n*:{3}$'

    icon_dict = {
        'primary': 'info-circle',
        'secondary': 'info-circle',
        'success': 'check-circle',
        'error': 'bug',
        'warning': 'warning',
        'info': 'info-circle'
    }

    def test(self, parent, block):
        return re.match(self.RE_FENCE_START, block)

    def run(self, parent, blocks):
        # print(blocks)
        original_block = blocks[0]
        first_blocks = original_block.split()
        if len(first_blocks) == 3:
            title = first_blocks[2]
        elif len(first_blocks) == 2:
            title = "Null"
        else:
            return False
        blocks[0] = re.sub(self.RE_FENCE_START, '', blocks[0])

        # Find block with ending fence
        for block_num, block in enumerate(blocks):
            if re.search(self.RE_FENCE_END, block):
                # remove fence
                blocks[block_num] = re.sub(self.RE_FENCE_END, '', block)
                # render fenced area inside a new div
                e = etree.SubElement(parent, 'div')
                icon_elm = etree.Element('i')
                strong_tag = etree.Element('strong')
                title_elm = etree.Element('p')
                class_value = 'alert alert-{}'
                flag = False
                for key in ['primary', 'secondary', 'success', 'error', 'warning', 'info']:
                    if key in original_block:
                        e.set('class', class_value.format(key))
                        e.set('role', 'alert')
                        icon_elm.set('class', 'fa fa-{}'.format(self.icon_dict[key]))
                        strong_tag.append(icon_elm)
                        span_elm = etree.Element('span')
                        span_elm.text = title
                        strong_tag.append(span_elm)
                        title_elm.append(strong_tag)
                        if title == 'Null':
                            pass
                        else:
                            e.insert(0, title_elm)
                        flag = True
                        break
                if not flag:
                    return False
                self.parser.parseBlocks(e, blocks[0:block_num + 1])
                # remove used blocks
                for i in range(0, block_num + 1):
                    blocks.pop(0)
                return True  # or could have had no return statement
        # No closing marker!  Restore and do nothing
        blocks[0] = original_block
        return False  # equivalent to our test() routine returning False


class AlertExtension(Extension):
    """
    Alert 拓展
    """
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(AlertBlockProcessor(md.parser), 'alert', 185)


class CustomFootNoteExtension(FootnoteExtension):
    """
    自定义脚注
    """
    def makeFootnotesDiv(self, root: etree.Element) -> etree.Element | None:
        """ Return `div` of footnotes as `etree` Element. """

        if not list(self.footnotes.keys()):
            return None

        div = etree.Element("div")
        div.set('class', 'footnote')
        etree.SubElement(div, "hr")
        ol = etree.SubElement(div, "ol")
        surrogate_parent = etree.Element("div")

        # Backward compatibility with old '%d' placeholder
        backlink_title = self.getConfig("BACKLINK_TITLE").replace("%d", "{}")

        for index, id in enumerate(self.footnotes.keys(), start=1):
            li = etree.SubElement(ol, "li")
            li.set("id", self.makeFootnoteId(id))
            # Parse footnote with surrogate parent as `li` cannot be used.
            # List block handlers have special logic to deal with `li`.
            # When we are done parsing, we will copy everything over to `li`.
            self.parser.parseChunk(surrogate_parent, self.footnotes[id])
            for el in list(surrogate_parent):
                li.append(el)
                surrogate_parent.remove(el)
            backlink = etree.Element("a")
            backlink.set("href", "#" + self.makeFootnoteRefId(id))
            backlink.set("class", "footnote-backref")
            backlink.set(
                "title",
                backlink_title.format(index)
            )
            backlink.text = FN_BACKLINK_TEXT

            if len(li):
                node = li[-1]
                if node.tag == "p":
                    node.text = "<span class='footnote-text'>" + node.text + "</span>\n" + NBSP_PLACEHOLDER
                    node.append(backlink)
                else:
                    p = etree.SubElement(li, "p")
                    p.append(backlink)
        return div

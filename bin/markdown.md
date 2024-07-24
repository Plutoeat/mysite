# 段落

这是第一段普通段落

这是第二段普通段落

# 标题

# 标题 1

## 标题 2

### 标题 3

#### 标题 4

##### 标题 5

###### 标题 6

# 列表

## 无序列表

- 列表 1
- 列表 2
- 列表 3

## 有序列表

1. 列表 1
2. 列表 2
3. 列表 3

# 引用解析

> 这是一段引用文字

# 代码块解析

## 行内代码块

在文本中引用`@radix-ui/react-alert-dialog`行内代码块

## 多行代码块

```python
def hello_world():
	print("hello world")
hello_world()
```

# 强调解析

*斜体*

**粗体**

~~删除线~~

==高亮==

<kbd>Enter</kbd>

icon:home

# 链接和图片解析

[百度](https://www.baidu.com)

<https://www.baidu.com>

![测试图片](/media/editor\1705243030087_20240710212026212435.jpg "测试图片标题")

# 表格解析

|  日期   |  金额  |  利息  |
| :----- | :----: | ----: |
| 2012.03 | ￥2000 | ￥2000 |
| 2012.04 | ￥2000 | ￥2000 |
| 2012.05 | ￥2000 | ￥2000 |
| 2012.06 | ￥2000 | ￥2000 |

# 代码高亮解析

字符==高亮==显示

# 脚注解析

这里有一个脚注[^1]。哈哈哈！

这里有一个脚注[^2]。哈哈哈！

[^1]: 这是脚注内容。你可以在这里提供额外的信息或参考资料

[^2]: 这是脚注内容。你可以在这里提供额外的信息或参考资料

# Admonition

!!! Info
    This is an info admonition.

!!! success
	This is a success admonition.

!!! warning
    This is a warning admonition.

!!! error
    This is an error admonition.

# 引用别名解析

This is an abbreviation HTML
*[HTML]:HyperText Markup Language

# 任务列表解析

- [ ] 事项1
- [ ] 事项2
- [x] 事项3

# 表情符号解析

插入表情符号:smile:

# 自定义标签解析

<font>默认标签</font>

<font style="background-color:cyan">自定义颜色标签</font>

details:折叠标签
青青子衿，悠悠我心
老骥伏枥，志在千里

<details>
    <summary>自定义折叠标签</summary>
    <div>
        <p>青青子衿，悠悠我心</p>
        <p>老骥伏枥，志在千里</p>
    </div>
</details>

# 公式块解析

行内$y=ax^2+bx+c$公式块

$$
y=ax^2+bx+c
$$

# 注释块解析

<!-- 这是个注释 -->

# 自定义Alert解析

::: info

这是一个没有标题的 alert
:::

::: info 注意

这是一个演示效果，~~我是被删除的内容~~
:::

::: info

🎉 **自定义标题**

这是一个没有标题的 alert
:::

::: secondary

这是一个没有标题的 alert
:::

::: success 注意

这是一个演示效果，~~我是被删除的内容~~
:::

::: error 注意

这是一个演示效果，~~我是被删除的内容~~
:::

::: warning 注意

这是一个演示效果，~~我是被删除的内容~~
:::
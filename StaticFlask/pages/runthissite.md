title: 'What Runs this Site'
published: '2015-12-08'

One of the problems I had when I first learnt how to programme was that I hated using other peoples' code. I guess I was falling for the [myth of the genius programmer](http://www.youtube.com/watch?v=0SARbwvhupQ). I truly felt that I had to understand everything, from the ground up, and obviosuly that made even the simplest tasks totally daunting. It wasn't until I joined [voXup](https://voXup.co.uk) that I got comfortable with building on existing platforms.

All that said, I do sort of believe that reinventing the wheel *a little bit* is an essential part of learning to code. And as such, this site is basically just that, a static-file blogging site kind of ike Jekyll, built using Python and Markdown.

<blockquote class="twitter-tweet" lang="en"><p lang="en" dir="ltr">&quot;I like this tool, but it&#39;s in the wrong language.&quot;&#10;&quot;Wait, what? Why does that even matter?&quot;&#10;&quot;Don&#39;t worry, I re-wrote it in Python.&quot;</p>&mdash; SecuriTay (@SwiftOnSecurity) <a href="https://twitter.com/SwiftOnSecurity/status/663574885671702530">November 9, 2015</a></blockquote>
<script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>

I really like Python. It was the language we used to build the backend of voXup, and since then it's been my go-to language for any code I've written outside of an academic setting. But, again, wanting to understand everything, I didn't feel like hosting all my personal projects on Google App Engine. (For one thing, it'd be complete overkill resource-wise.) So, last year, I started messing around with [Flask](https://flask.pocoo.org), using it to build a dumb little site that would Yo you walking directions to the nearest tube-stop.

What I like about Flask is that it keeps everything simple. Similarly to how App Engine works, you can define everything in one file if you feel like it, unlike the strict regimenting of a Django project, and there's very little required to get started. A 'Hello, world' in flask looks like this:
```python
from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello():
    return 'Hello, world!'

if __name__ == '__main__':
    app.run()
```

It's still only version 0.10, but Flask already has a lot of [extensions](http://flask.pocoo.org/extensions/) available that add a tonne of functionality. Thanks to two of these addons, this site is less than a 100 lines of code!

I decided early on that I wanted to be able to write posts in Markdown, and so I use `Flask-FlatPages` to render the files as HTML, and then pass these objects into my templates. That's as simple as adding
```python
pages = Pages(app)
```
give or take a couple of config flags to point to where the markdown files are on disk. The `pages` object is then a generator with all your pages in it as objects ready to be passed in to Jinja and rendered just by adding `{{page}}`!

I also decided (again, as I wanted to do absolutely everything in this project) that I was going to self-host, using my old Raspberry Pi Model-B (with 256MB of RAM; it's an *old* Pi). So, to keep things light, I figured this would be a static-file site, pre-rendering all the pages so they can be served up quickly with nginx. `Frozen-Flask` came to the rescue with exactly the functionality I needed.

This took a little bit more configuration than `FlatPages` to get going, mostly to configure pagination on the main index which is sort of putting the cart before the horse as this blog has almost no content as it stands. 
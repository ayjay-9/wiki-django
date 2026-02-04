import markdown2
import random
import re

from django.shortcuts import redirect, render

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# View function for displaying an encyclopedia entry
# If the requested entry does not exist, render an error page, otherwise render the entry page with the entry's content
def entry(request, title):
    entry = util.get_entry(title)
    if entry is None:
        # return HttpResponseRedirect()
        return render(request, "encyclopedia/error.html", {
            "message": "The requested page was not found."
        })
    else:
        # Split the entry into title and body, and clean the title for display
        title, body = entry.split("\n", 1)
        clean_title = title.lstrip("# ").strip()
        # Convert the body from Markdown to HTML and render the entry page
        html_body = markdown2.markdown(body.strip())
        return render(request, "encyclopedia/entry.html", {
            "title": clean_title,
            "entry": html_body,
        })

# View function for handling search requests
# If the search query matches an existing entry, redirect to that entry's page
# Otherwise, display a list of entries that contain the search query as a substring
def search(request):
    query = request.GET.get("q", "")
    entries = util.list_entries()
    if query in entries:
        return entry(request, query)
    else:
        results = [entry for entry in entries if query.lower() in entry.lower()]
        return render(request, "encyclopedia/search_results.html", {
            "query": query,
            "results": results,
        })
    
# View function to allow users to create a new encyclopedia entry by entering a title, and content 
# in a textarea
def new_page(request):
    if request.method == "POST":
        # Get the title and content from the form submission
        raw_title = request.POST.get("title").strip()
        title = raw_title.lstrip("# ").strip()

        content = request.POST.get("content", "")
        # Check if an entry with the same title already exists
        entries = util.list_entries()

        if title.lower() in (entry.lower() for entry in entries):
            return render(request, "encyclopedia/error.html", {
                "message": "An entry with this title already exists."
            })
        else:
            # Save the new entry and redirect to its page
            util.save_entry(title, f"# {title}\n\n{content}")
            return redirect("encyclopedia:entry", title=title)
    else:
        # If the request method is GET, render the new page form
        return render(request, "encyclopedia/new_page.html")
    
# View function to allow users to edit an existing encyclopedia entry
def edit_page(request, title):
    entry = util.get_entry(title)
    # If the entry does not exist, render an error page
    if entry is None:
        return render(request, "encyclopedia/error.html", {
            "message": "The requested page was not found."
        })
    
    linked_title, body = entry.split("\n", 1)
    clean_title = linked_title.lstrip("# ").strip()
    body = body.lstrip("\n")
    
    # If the request method is POST, save the edited content
    if request.method == "POST":
        # Get the updated content from the form submission
        content = request.POST.get("content", "")
        content = content.replace("\r\n", "\n")  # Normalize line endings
        content = content.strip() # Remove leading/trailing whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)  # Replace multiple newlines with one newlines

        # Save the updated entry and redirect to its page
        util.save_entry(clean_title, f"# {clean_title}\n\n{content}")
        
        # Redirect to the updated entry page
        return redirect("encyclopedia:entry", title=clean_title)
    else:
        # If the request method is GET, render the edit page form with current content
        return render(request, "encyclopedia/edit_page.html", {
            "title": clean_title,
            "content": body,
        })
    
# View function to display a random encyclopedia entry
def random_entry(request):
    entries = util.list_entries()
    random_title = random.choice(entries)
    return redirect("encyclopedia:entry", title=random_title)
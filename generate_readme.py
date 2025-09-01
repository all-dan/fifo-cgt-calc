import inspect
import normalization
import app
import fifo

# --- Marker Definition
start_marker = "<!-- FUNCTION_REFERENCE_START -->"
end_marker = "<!-- FUNCTION_REFERENCE_END -->"

# --- List of modules to document
scripts = [normalization, app, fifo]

# --- New Content to Insert
func_docs = ""

# -- Loop through all scripts to get doc-strings
for script in scripts:
    func_docs += f'### Module: {script.__name__}.py\n\n'
    # For every function in a module, extract its documentation
    for name, func in inspect.getmembers(script, inspect.isfunction):
        func_docs += f'#### `{name}{inspect.signature(func)}` \n\n {inspect.getdoc(func)} \n\n'

# --- Read the existing README content
with open("README.md", "r") as f:
    content = f.read()

# --- Find the markers
start = content.find(start_marker) + len(start_marker)
end = content.find(end_marker)

# --- Replace the content between the markers
if start != -1 and end != -1:
    new_content = (
        content[:start] +
        "\n\n" +
        func_docs +
        "\n\n" +
        content[end:]
    )
    with open("README.md", "w") as f:
        f.write(new_content)
else:
    print("Markers not found.")
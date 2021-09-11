from citywok_ms import create_app
import os

app = create_app(
    instance_name="saojoao",
    instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), "saojoao"),
)

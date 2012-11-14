# py-ninja Examples

(in order of complexity)

* `button_pushed.py` - basic example, using the button
* `log_temperature.py` - recording a single device's data to a file
* `multiple_devices_using_watcher.py` - multiple devices printing data, using a Watcher
* `multiple_devices_with_nodes.py` - complex data flow with multiple devices, using Nodes

To run, install `py-ninja`, or at least the requirements since the examples will look in the project directory for the `ninja` package, and add keys and IDs to a `secrets.py` file in the `/examples` directory. Then, `python <example_file>` will run the examples.
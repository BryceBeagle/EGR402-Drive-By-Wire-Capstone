from flask import Flask, request, render_template
from gpio  import Controller, OUTPUT

app = Flask(__name__)


Controller.available_pins = [398, 298, 389, 388]

pin_map = {0 : Controller.alloc_pin(398, OUTPUT),
           1 : Controller.alloc_pin(298, OUTPUT),
           2 : Controller.alloc_pin(389, OUTPUT),
           3 : Controller.alloc_pin(388, OUTPUT)}


def set_gpio(pin_number, value):

    if value:
        pin_map[pin_number].set()
    else:
        pin_map[pin_number].reset()


@app.route("/")
def form():

    print("Hello")

    return render_template('led_checkboxes.html')


@app.route("/", methods=['POST'])
def form_post():
    led0 = request.form.get('led0')
    led1 = request.form.get('led1')
    led2 = request.form.get('led2')
    led3 = request.form.get('led3')

    for i, val in enumerate([led0, led1, led2, led3]):

        val = 0 if val is None else val

        print("Setting LED{} to {}".format(i, val))

        set_gpio(i, val)

    return render_template('led_checkboxes.html')


if __name__ == "__main__":

    port = 5000
    app.run(debug=True, port=port, host='0.0.0.0')

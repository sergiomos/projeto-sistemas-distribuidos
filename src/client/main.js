const zmq = require("zeromq")

async function run() {
  const sock = new zmq.Request()

  sock.connect("tcp://broker:5555")
  console.log("Producer bound to port 5555")

  await sock.send("4")
  const result = await sock.receive()

  console.log(result)
}

run()

"use strict";

module.exports = function(RED) {
    const fs = require('fs');
    const ini = require('ini');
    const sdk = require('iotconnect-sdk-tpm');
    const util = require('util');
    const { execFileSync } = require('child_process');
    const config_file = '/opt/avnet-iot/IoTConnect/sample/expressconnect';
    const qa_delay = 90 * 1000;   // milliseconds between sends (90 seconds..)
    const prod_delay = 500;       // milliseconds between sends (.5 seconds..)

    let server = false;
    let active_nodes = 0;
    let uniqueId = "";
    let connected = false;
    let final_done = false;
    let attributes = false;
    let twins = false;

    let send_queue = [];
    let next_send_time = 0;
    let send_delay = qa_delay;
    let logged_notconnected_message = false;
    let verbose_logging = false;

    function IoTConnectNode(config) {
        RED.nodes.createNode(this, config);
        var node = this;
        node.log('IoT Connect Node');
        verbose_logging = fs.existsSync('/tmp/debug-node');

        var twinMessageCallback = function(data) {
            for (var key in data.desired) {
                if (key != '$version') {
                    node.log(`Twin '${key}' to '${data.desired[key]}'`)
                    server.updateTwin(key, data.desired[key]);
                }
            }
        };

	var unscheduled_disconnect = function() {
	    return active_nodes > 0;
	}

        var validData = function(data) {
            return data != null && data != undefined &&
                data.ack != undefined && data.cmdType != null;
        };

        var messageCallback = function(data) {
            if (!validData(data)) {
                console.log('Message Callback data not valid:',
                            util.inspect(data, false, null));
                return;
            }

            node.log(`message callback '${data.cmdType}'`);
            switch (data.cmdType) {
            case '0x01':
                // Device command
                node.log(`command: '${data.command}'`);
                if (data.ack && data.ackId != null) {
                    server.sendAck({"ackId":data.ackId, "st":6}, new Date(), 5);
                }
                break;
            case '0x02':
                // Firmware OTA command
                if (data.ack && data.ackId != null) {
                    node.log("message callback ${data.cmdType}: sending Ack");
                    server.sendAck({"ackId":data.ackId, "st":7}, new Date(), 11);
                }
                break;
            case '0x16':
                // Connection Status
                if (data.command) {
                    connected = true;
                    logged_notconnected_message = false;
                    node.log("Server Connected");

                    if (!twins) {
                        node.log("Requesting Twins");
                        server.getAllTwins();
                        twins = true;
                    }

                    if (!attributes) {
                        node.log("Requesting Attributes");
                        server.getAttributes(function(response) {
                            if (response.status) {
                                node.log("Got Attributes");
                                let a = response.data[0].attributes;
                                // [
                                //    { ln: 'skin_temp', dt: 'number', dv: '' },
                                //    { ln: 'cpu_temp', dt: 'number', dv: '' }
                                // ]
                                // node.log(util.inspect(a, false, null));
                                attributes = {}
                                for (let k in a)
                                    if ('ln' in a[k] && 'dt' in a[k])
                                        attributes[a[k]['ln']] = a[k]['dt'];
                                node.log(util.inspect(attributes, false, null));
                            }
                        });
                    }
                } else {
                    node.log("Server Disconnected");
		    node.log(`Active nodes: ${active_nodes}`);
		    node.log(`(was) Connected: ${connected}`);
		    node.log(`Final Done ${final_done}`);
		    if (unscheduled_disconnect()) {
			// Server disconnect
			// Server down?
			// Bad connectivity?
			// Or device instance removed by app or portal?
			try {
			    execFileSync('/opt/avnet-iot/iotservices/express-device-status');
			} catch (e) {
			    node.log(util.inspect(e, false, null));
			}
		    }
                    connected = false;
                    twins = false;
                    attributes = false;
                    server = false;
                    if (final_done) {
                        final_done();
                        final_done = false;
                    }
                }
                break;
            default:
                node.warn(`Unhandled cmdType: ${data.cmdType}`);
            }
        };

        node.on('input', function(msg, send, done) {
            if (attributes) {
                if ("sensorId" in msg &&
                    "payload" in msg &&
                    msg.sensorId in attributes &&
                    typeof msg.payload === attributes[msg.sensorId]) {
                    if (verbose_logging) {
                        node.log(`input: '${msg.sensorId}': ${msg.payload}`);
                    }
                    send_queue.push({
                        "uniqueId": uniqueId,
                        "time": new Date().toISOString(),
                        "data": {
                            [msg.sensorId]: msg.payload
                        },
                    });
                } else {
                    if (verbose_logging) {
                        node.log(`INVALID MSG: '${util.inspect(msg, false, null)}`);
                    }
                }
            }

            if (server && connected) {
                if (Date.now() >= next_send_time) {
                    if (verbose_logging) {
                        node.log(`sendData: with ${send_queue.length} items`);
                    }
                    server.sendData(send_queue);
                    send_queue = [];
                    next_send_time = Date.now() + send_delay;
                }
            } else {
                if (!logged_notconnected_message) {
                    done('Attempt to send data, but server is not connected');
                    logged_notconnected_message = true;
                    return;
                }
            }
            done();
        });

        node.on('close', function(removed, done) {
            active_nodes--;
            if (active_nodes === 0 && server && connected) {
                final_done = done;
                server.dispose();
            } else {
                done();
            }
            logged_notconnected_message = false;
        });

        active_nodes++;
        if (!server) {
            // read these from a file.
            var params = ini.parse(fs.readFileSync(config_file, 'utf-8'));
            var apienv   = params.default.apienv;
            var cpid     = params.default.cpid;
            var scopeId  = params.default.scopeId;
            uniqueId     = params.default.uniqueId;

            // Make isDebug an option somehow. Twin? Env? Configfile?
            var sdkOptions = { "isDebug": fs.existsSync('/tmp/debug-sdk') };

            if (apienv === "qa") {
                send_delay = qa_delay;
            } else {
                send_delay = prod_delay;
            }

            server = new sdk(cpid, uniqueId, scopeId,
                             messageCallback, twinMessageCallback,
                             sdkOptions, apienv);
        }
    };

    RED.nodes.registerType("iotconnect", IoTConnectNode);
};

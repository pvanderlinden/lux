//  Grid Data Provider
//	===================
//
//	provides data to a lux.grid using websockets

angular.module('lux.grid.dataProviderWebsocket', ['lux.sockjs'])
    .factory('GridDataProviderWebsocket', ['$rootScope', '$timeout', gridDataProviderWebsocketFactory]);

function gridDataProviderWebsocketFactory ($scope, $timeout) {

    function GridDataProviderWebsocket(websocketUrl, channel, listener) {
        this._websocketUrl = websocketUrl;
        this._channel= channel;
        this._listener = listener;
    }

    function onMessage(sock, msg) {
        /*jshint validthis:true */
        var tasks;

        if (msg.event === 'record-update') {
            tasks = msg.data;

            this._listener.onDataReceived({
                total: msg.total,
                result: tasks,
                type: 'update'
            });

        } else if (msg.event === 'records') {
            tasks = msg.data;

            this._listener.onDataReceived({
                total: msg.total,
                result: tasks,
                type: 'update'
            });

            $timeout(sendFakeRecordOnce.bind(this), 0); // TODO Remove this. It's a dummy status update for development.

        } else if (msg.event === 'columns-metadata') {
            this._listener.onMetadataReceived(msg.data);
        }
    }


    GridDataProviderWebsocket.prototype.destroy = function() {
        this._listener = null;
    };

    GridDataProviderWebsocket.prototype.connect = function() {
        checkIfDestroyed.call(this);

        function onConnect(sock) {
            /*jshint validthis:true */
            this.getPage();
        }

        this._sockJs = $scope.sockJs(this._websocketUrl);

        this._sockJs.addListener(this._channel, onMessage.bind(this));

        this._sockJs.connect(onConnect.bind(this));

        // TODO Remove this. It's a dummy status update for development.
        var sendFakeRecordOnce = function() {
            /* jshint validthis:true */
            this._listener.onDataReceived({
                total: 100,
                result: [{
                    args: "[]",
                    eta: 1440517140003.5932,
                    hostname: "gen25880@oxygen.bmll.local",
                    kwargs: "{}",
                    name: "bmll.server_status",
                    status: "sent",
                    timestamp: 1440517140003.5932,
                    uuid: "fa5b8e1b-2be7-4ec5-a7a6-f3c82db14117",
                    result: "12:24:47 [p=20856, t=2828, ERROR, concurrent.futures] exception calling callback for <Future at 0x71854a8 state=finished raised RuntimeError>\n" +
"Traceback (most recent call last):\n" +
"  File \"c:\Python34\lib\concurrent\futures\thread.py\", line 54, in run\n" +
"    result = self.fn(*self.args, **self.kwargs)\n" +
"  File \"c:\Users\jeremy\Git\bmll\bmll-api\bmll\monitor\celeryapp.py\", line 179, in _receive_events\n" +
"    self._next_event_call(self.polling_interval, self._receive_events)\n" +
"  File \"c:\Users\jeremy\Git\bmll\bmll-api\bmll\monitor\celeryapp.py\", line 166, in _next_event_call\n" +
"    callable)\n" +
"  File \"c:\Python34\lib\asyncio\base_events.py\", line 462, in call_soon_threadsafe\n" +
"    handle = self._call_soon(callback, args)\n" +
"  File \"c:\Python34\lib\asyncio\base_events.py\", line 436, in _call_soon\n" +
"    self._check_closed()\n" +
"  File \"c:\Python34\lib\asyncio\base_events.py\", line 265, in _check_closed\n" +
"    raise RuntimeError('Event loop is closed')\n" +
"RuntimeError: Event loop is closed\n" +
"\n" +
"During handling of the above exception, another exception occurred:\n" +
"\n" +
"Traceback (most recent call last):\n" +
"  File \"c:\Python34\lib\concurrent\futures\_base.py\", line 297, in _invoke_callbacks\n" +
"    callback(self)\n" +
"  File \"c:\Python34\lib\asyncio\futures.py\", line 408, in <lambda>\n" +
"    new_future._copy_state, future))\n" +
"  File \"c:\Python34\lib\asyncio\base_events.py\", line 462, in call_soon_threadsafe\n" +
"    handle = self._call_soon(callback, args)\n" +
"  File \"c:\Python34\lib\asyncio\base_events.py\", line 436, in _call_soon\n" +
"    self._check_closed()\n" +
"  File \"c:\Python34\lib\asyncio\base_events.py\", line 265, in _check_closed\n" +
"    raise RuntimeError('Event loop is closed')\n" +
"RuntimeError: Event loop is closed,\n" +
"Traceback (most recent call last):\n" +
"  File \"c:\Python34\lib\concurrent\futures\thread.py\", line 54, in run\n" +
"    result = self.fn(*self.args, **self.kwargs)\n" +
"  File \"c:\Users\jeremy\Git\bmll\bmll-api\bmll\monitor\celeryapp.py\", line 179, in _receive_events\n" +
"    self._next_event_call(self.polling_interval, self._receive_events)\n" +
"  File \"c:\Users\jeremy\Git\bmll\bmll-api\bmll\monitor\celeryapp.py\", line 166, in _next_event_call\n" +
"    callable)\n" +
"  File \"c:\Python34\lib\asyncio\base_events.py\", line 462, in call_soon_threadsafe\n" +
"    handle = self._call_soon(callback, args)\n" +
"  File \"c:\Python34\lib\asyncio\base_events.py\", line 436, in _call_soon\n" +
"    self._check_closed()\n" +
"  File \"c:\Python34\lib\asyncio\base_events.py\", line 265, in _check_closed\n" +
"    raise RuntimeError('Event loop is closed')\n" +
"RuntimeError: Event loop is closed\n" +
"\n" +
"During handling of the above exception, another exception occurred:\n" +
"\n" +
"Traceback (most recent call last):\n" +
"  File \"c:\Python34\lib\concurrent\futures\_base.py\", line 297, in _invoke_callbacks\n" +
"    callback(self)\n" +
"  File \"c:\Python34\lib\asyncio\futures.py\", line 408, in <lambda>\n" +
"    new_future._copy_state, future))\n" +
"  File \"c:\Python34\lib\asyncio\base_events.py\", line 462, in call_soon_threadsafe\n" +
"    handle = self._call_soon(callback, args)\n" +
"  File \"c:\Python34\lib\asyncio\base_events.py\", line 436, in _call_soon\n" +
"    self._check_closed()\n" +
"  File \"c:\Python34\lib\asyncio\base_events.py\", line 265, in _check_closed\n" +
"    raise RuntimeError('Event loop is closed')\n" +
"RuntimeError: Event loop is closed,\n"
                }],
                type: 'update'
            });

        sendFakeRecordOnce = function() {};
        };

    };

    GridDataProviderWebsocket.prototype.getPage = function(options) {
        var waitForRequest = function() {
            console.log('waiting for request');
            var promise = $timeout(function() {
                console.log('TIMEOUT!');
            }, 20000);

            return function(data) {
                console.log('request complete', arguments);
                $timeout.cancel(promise);
                onMessage({}, JSON.parse(data)).bind(this);
            };
        }.bind(this);

        this._sockJs.rpc(this._channel, {}, waitForRequest());
    };

    GridDataProviderWebsocket.prototype.deleteItem = function(identifier, onSuccess, onFailure) {
        // not yet implemented
    };

    function checkIfDestroyed() {
        /* jshint validthis:true */
        if (this._listener === null || typeof this._listener === 'undefined') {
            throw 'GridDataProviderREST#connect error: either you forgot to define a listener, or you are attempting to use this data provider after it was destroyed.';
        }
    }

    return GridDataProviderWebsocket;
}

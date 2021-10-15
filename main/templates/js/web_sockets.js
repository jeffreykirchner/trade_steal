//web sockets, needs should be included with companion vue.js app
doWebSockets = function()
{
        var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
        app.$data.chatSocket = new WebSocket(            
                               ws_scheme + '://' + window.location.host +
                               '/ws/{{websocket_path}}/{{channel_key}}/{{page_key}}');        
    
        app.$data.chatSocket.onmessage = function(e) {
            var data = JSON.parse(e.data);                       
            app.takeMessage(data);
        };
    
        app.$data.chatSocket.onclose = function(e) {
            console.error('Socket closed, trying to connect ... ');
            app.$data.reconnecting=true;
            window.setTimeout(doWebSockets(), randomNumber(500,1500));            
        }; 

        app.$data.chatSocket.onopen = function(e) {
            console.log('Socket connected.');     
            app.$data.reconnecting=false;   
            app.handleSocketConnected();                      
        };                
};

randomNumber = function(minimum,maximum){
    //return a random number between min and max
    return (Math.random() * (maximum - minimum + 1) );
};

doWebSockets();
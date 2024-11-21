//web sockets, needs should be included with companion vue.js app
doWebSockets = function()
{
        var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
        app.chatSocket = new WebSocket(            
                               ws_scheme + '://' + window.location.host +
                               '/ws/{{websocket_path}}/{{channel_key}}/{{page_key}}/{{player_key}}');        
    
        app.chatSocket.onmessage = function(e) {
            var data = JSON.parse(e.data);                       
            app.take_message(data);
        };
    
        app.chatSocket.onclose = function(e) {
            console.error('Socket closed, trying to connect ... ');
            app.reconnecting=true;

            if(!app.handle_socket_connection_try()) 
            {
                console.error('Socket re-connection limit reached.');
                return;
            } 

            window.setTimeout(doWebSockets(), randomNumber(500,1500));            
        }; 

        app.chatSocket.onopen = function(e) {
            console.log('Socket connected.');     
            app.reconnecting=false;   
            app.handle_socket_connected();                      
        };                
};

randomNumber = function(min, max){
    //return a random number between min and max
    min = Math.ceil(min);
    max = Math.floor(max+1);
    return Math.floor(Math.random() * (max - min) + min);
};

doWebSockets();
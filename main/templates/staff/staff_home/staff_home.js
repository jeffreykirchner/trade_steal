
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

//vue app
var app = Vue.createApp({
    delimiters: ["[[", "]]"],

    data() {return {chatSocket : "",
                    reconnecting : true,
                    working : false,
                    sessions : [],
                    createSessionButtonText : 'Create Session <i class="fas fa-plus"></i>',
                    dateSortButtonText: 'Date <i class="fas fa-sort"></i>',
                    titleSortButtonText: 'Title <i class="fas fa-sort"></i>',
                }},
    methods: {
        handleSocketConnected(){
            //fire when socket connects
            app.sendGetSessions();
        },

        takeMessage(data) {
           //process socket message from server

           console.log(data);

           messageType = data.message.messageType;
           messageData = data.message.messageData;

            switch(messageType) {
                case "create_session":
                    app.takeCreateSession(messageData);
                    break;
                case "get_sessions":
                    app.takeGetSessions(messageData);
                    break;
    
            }

            app.working = false;
        },

        sendMessage(messageType,messageText) {
            //send socket message to server

            app.$data.chatSocket.send(JSON.stringify({
                    'messageType': messageType,
                    'messageText': messageText,
                }));
        },

        sendCreateSession(){
            //send create new session
            app.$data.createSessionButtonText ='<i class="fas fa-spinner fa-spin"></i>';
            app.sendMessage("create_session",{});
        },

        takeCreateSession(messageData){
            //take create new session
            app.$data.createSessionButtonText ='Create Session <i class="fas fa-plus"></i>';
            app.takeGetSessions(messageData);
        },

        sendGetSessions(){
            //get list of sessions
            app.sendMessage("get_sessions",{});
        },

        takeGetSessions(messageData){
            //process list of sessions

            app.sessions = messageData.sessions;
            
        },

        sendDeleteSession(id){
            //delete specified session
            app.working = true;
            app.sendMessage("delete_session",{"id" : id});
        },
        
    },

    mounted(){
        
    },

}).mount('#app');

{%include "js/web_sockets.js"%}

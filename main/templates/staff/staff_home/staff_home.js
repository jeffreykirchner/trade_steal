
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

//vue app
var app = Vue.createApp({
    delimiters: ["[[", "]]"],

    data() {return {chatSocket : "",
                    reconnecting : true,
                    working : false,
                    helpText : "Loading ...",
                    sessions : [],
                    sessions_full_admin : [],
                    sessions_full_admin_visible : false,
                    createSessionButtonText : 'Create Session <i class="fas fa-plus"></i>',
                    dateSortButtonText: 'Date <i class="fas fa-sort"></i>',
                    titleSortButtonText: 'Title <i class="fas fa-sort"></i>',
                }},
    methods: {
        handleSocketConnected: function handleSocketConnected(){
            //fire when socket connects
            app.sendGetSessions();
        },

        takeMessage: function takeMessage(data) {
           //process socket message from server

           {%if DEBUG%}
           console.log(data);
           {%endif%}

           messageType = data.message.messageType;
           messageData = data.message.messageData;

            switch(messageType) {
                case "create_session":
                    app.takeCreateSession(messageData);
                    break;
                case "get_sessions":
                    app.take_get_Sessions(messageData);
                    break;
                case "get_sessions_admin":
                    app.take_get_SessionsAdmin(messageData);
                    break;
    
            }

            app.working = false;
        },

        sendMessage: function sendMessage(messageType, messageText, message_target="self") {
            //send socket message to server

            this.chatSocket.send(JSON.stringify({
                    'messageType': messageType,
                    'messageText': messageText,
                    'message_target': message_target,
                }));
        },

        sendGetSessions: function sendGetSessions(){
            //get list of sessions
            app.sendMessage("get_sessions",{});
        },

        take_get_Sessions: function take_get_Sessions(messageData){
            //process list of sessions

            app.sessions = messageData.sessions;

            if(this.sessions_full_admin_visible)
            {
                app.sendGetSessionsAdmin()
            }
            
        },       

        formatDate: function(value){
            if (value) {        
                //console.log(value);                    
                return moment(String(value)).local().format('MM/DD/YYYY');
            }
            else{
                return "date format error";
            }
        },
        
        {%include "staff/staff_home/sessions_card_full_admin.js"%}
        {%include "staff/staff_home/sessions_card.js"%}
    },

    mounted(){
        
    },

}).mount('#app');

{%include "js/web_sockets.js"%}

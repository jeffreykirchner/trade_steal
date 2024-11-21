/**
 * update producton slider values when slider is moved
 */
update_production_slider: function update_production_slider(){

    // production_slider : 0,
    // production_slider_one : 50,
    // production_slider_two : 50,

    if(app.production_slider < 0){

        app.production_slider_one = Math.abs(app.production_slider) + 50;
        app.production_slider_two = 100 - app.production_slider_one;

    }else if(app.production_slider > 0){

        app.production_slider_two = Math.abs(app.production_slider) + 50;
        app.production_slider_one = 100 - app.production_slider_two;

    }else{
        app.production_slider = 0;
        app.production_slider_one = 50;
        app.production_slider_two = 50;
    }

},

/**
 * send prouduction rate updates
 */
sendProdution: function sendProdution(){

    if(app.working) return;
    
    app.working = true;
    app.send_message("production_time", 
                    {"production_slider_one" : app.production_slider_one,
                     "production_slider_two" : app.production_slider_two,},
                    "group");                   
},

/** take result of production rate updates
*/
takeProduction: function takeProduction(message_data){

    if(message_data.value == "success")
    {
        result = message_data.result;       
        
        app.session_player.good_one_production_rate = result.good_one_production_rate;
        app.session_player.good_two_production_rate = result.good_two_production_rate;
    } 
    else
    {
        
    }

    if(parseInt(message_data.session_player_id) == app.session_player.id)
    {
        app.working = false;           
    }
},
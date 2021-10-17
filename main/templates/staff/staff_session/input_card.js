
/**submit bid or offer
*/
submit_bid_offer:function(){
    app.$data.working = true;
    app.sendMessage("submit_bid_offer",{"bid_offer_id" : app.$data.bid_offer_id,
                                        "bid_offer_amount" : app.$data.bid_offer_amount,
                                        "sessionID" : app.$data.sessionID});
},

/**take result of submiting bid or offer
 * @param messageData {json} result of bid or offer
*/
take_submit_bid_offer:function(messageData){
    
    if(messageData.result.status == "success")
    {

        current_period = app.$data.session.current_period - 1;

        if (messageData.result.bid_list != null)
        {
            app.$data.session.session_periods[current_period].bid_list = messageData.result.bid_list;
        }
        else if(messageData.result.offer_list != null)
        {
            app.$data.session.session_periods[current_period].offer_list = messageData.result.offer_list;
        }

        app.$data.session.session_periods[current_period].current_best_offer = messageData.result.current_best_offer;
        app.$data.session.session_periods[current_period].current_best_bid = messageData.result.current_best_bid;
        app.$data.session.session_periods[current_period].trade_list = messageData.result.trade_list;

        if(messageData.result.realized_gains_from_trade != -1)
        {
            app.$data.session.session_periods[current_period].realized_gains_from_trade = messageData.result.realized_gains_from_trade;
            app.$data.session.session_periods[current_period].efficiency = messageData.result.efficiency;
        }

        app.$data.bid_offer_id = "";
        app.$data.bid_offer_amount = "";

        app.$refs.bid_offer_id.focus();
    }
    else
    {

    }

    app.$data.bid_offer_message = messageData.result.message;
},


/**undo last bid or offer
*/
undo_bid_offer:function(){
    app.$data.working = true;
    app.sendMessage("undo_bid_offer",{"sessionID" : app.$data.sessionID});
},

/**take result of undoing bid or offer
 * @param messageData {json} result of bid or offer
*/
take_undo_bid_offer:function(messageData){

    current_period = app.$data.session.current_period - 1;

    app.$data.session.session_periods[current_period].bid_list = messageData.result.bid_list;
    app.$data.session.session_periods[current_period].offer_list = messageData.result.offer_list;
    app.$data.session.session_periods[current_period].current_best_offer = messageData.result.current_best_offer;
    app.$data.session.session_periods[current_period].current_best_bid = messageData.result.current_best_bid;
    app.$data.session.session_periods[current_period].trade_list = messageData.result.trade_list;
    app.$data.bid_offer_message = messageData.result.message;
},

/**change the period being shown during replay
*/
updateCurrentPeriodReplay(adjustment){
    
    if(adjustment == 1)
    {
        if(app.$data.current_visible_period < app.$data.session.parameter_set.number_of_periods)
        {
            app.$data.current_visible_period += 1;
        }
    }
    else
    {
        if(app.$data.current_visible_period > 1)
        {
            app.$data.current_visible_period -= 1;
        }
    }

    app.$data.session.current_period =  app.$data.current_visible_period;

    Vue.nextTick(app.update_sdgraph_canvas());
},

/** start playback
 **/
playback_start(){
    app.$data.playback_enabled=true;
    app.$data.playback_trade=0;

    Vue.nextTick(app.update_sdgraph_canvas());
},

/** advance playback period in direction specified
 **/
 playback_advance(direction){
    if(direction == 1 && 
       app.$data.playback_trade < app.$data.session.session_periods[app.$data.current_visible_period-1].trade_list.length-1)
    {
        app.$data.playback_trade++;
    }
    else if (direction == -1 && app.$data.playback_trade > 0)
    {
        app.$data.playback_trade--;
    }

    Vue.nextTick(app.update_sdgraph_canvas());
},

/** start playback
 * */
 playback_stop(){
    app.$data.playback_enabled=false;

    Vue.nextTick(app.update_sdgraph_canvas());
},


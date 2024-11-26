/**
 * timer stopped warning
 */
show_timer_warning: function show_timer_warning(){
    if(app.session.timer_running)
    {
        app.timer_warning = true;
    }
},
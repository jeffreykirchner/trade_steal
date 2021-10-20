/**refresh the supply and demand canvas
*/
update_sdgraph_canvas:function(){

    var el = $('#sd_graph');
    el.attr('width', parseInt(el.css('width')));
    el.attr('height', parseInt(el.css('height')));

    //clear canvas
    app.clear_canvas();

    
},

/** clear canvas of current image to be re-drawn
 */
clear_canvas: function(chartID){
    if(document.getElementById(chartID) == null)
    {
        return;
    }

    var canvas = document.getElementById(chartID),
        ctx = canvas.getContext('2d');

    ctx.clearRect(0,0,w,h);
},
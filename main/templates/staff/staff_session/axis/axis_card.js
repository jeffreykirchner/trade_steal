/**refresh the supply and demand canvas
*/
update_sdgraph_canvas:function(){

    var el = document.getElementById('sd_graph');
    el.setAttribute('width', el.clientWidth);
    el.setAttribute('height', el.clientHeight);

    period = app.session.parameter_set.periods[app.current_visible_period-1];  //parameter set period
    period_result = app.session.session_periods[app.current_visible_period-1]; //session results period

    value_list = period.demand;
    cost_list = period.supply;

    y_max = period.y_scale_max;
    x_max = period.x_scale_max;

    var marginY=45;    //margin between left side of canvas and Y axis
    var marginX=40;    //margin between bottom of canvas and X axis
    var marginTopAndRight=10;    // margin between top and right sides of canvas and graph

    //clear canvas
    app.clear_canvas();

    //gains from trade fill
    if (app.session.started && app.show_gains_from_trade_graph)
    {
        app.draw_gain_from_trade_fill("sd_graph", marginY, marginX, marginTopAndRight, 0, y_max, 0, x_max, period, period_result.realized_gains_from_trade);
    }

    //playback gains fill
    if (app.playback_enabled)
    {
        app.draw_playback("sd_graph", marginY, marginX, marginTopAndRight, 0, y_max, 0, x_max, 3);
    }

    //axis
    app.draw_axis("sd_graph", marginY, marginX, marginTopAndRight, 0, y_max, y_max, 0, x_max, x_max, "Price ($)", "Units Traded");

    //bids and offers
    if (app.session.started && app.show_bids_offers_graph)
    {
        app.draw_bids_and_offers("sd_graph", marginY, marginX, marginTopAndRight, 0, y_max, 0, x_max, period_result);
    }

    if (app.show_supply_demand_graph)
    {
        //supply
        app.draw_sd_line("sd_graph", marginY, marginX, marginTopAndRight, 0, y_max, 0, x_max, 3, value_list, "cornflowerblue");

        //demand
        app.draw_sd_line("sd_graph", marginY, marginX, marginTopAndRight, 0, y_max, 0, x_max, 3, cost_list, "crimson");
    }

    //equilibrium
    if (app.show_equilibrium_price_graph)
    {
        app.draw_eq_lines("sd_graph", marginY, marginX, marginTopAndRight, 0, y_max, 0, x_max, period);
    }

    //trade line
    if (app.show_trade_line_graph)
    {
        app.draw_trade_line("sd_graph", marginY, marginX, marginTopAndRight, 0, y_max, 0, x_max, period_result);
    }

    //key
    if (!app.session.finished)
    {
        app.draw_key("sd_graph", marginTopAndRight, period_result);
    }

    //gains from trade key
    if (app.show_gains_from_trade_graph)
    {
        app.draw_grains_from_trade("sd_graph", marginTopAndRight, period_result);
    }

    //price cap
    app.draw_price_cap("sd_graph", marginY, marginX, marginTopAndRight, 0, y_max, 0, x_max, period);
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

/**draw an x-y axis on a canvas
 * @param chartID {string} dom ID name of canvas
 * @param marginY {int} margin between Y axis and vertial edge of graph
 * @param marginX {int} margin between X axis and horizontal edge of graph
 * @param marginTopAndRight {int} margin between top and rights side of canvas and graph
 * @param yMin {int} starting value on Y axis
 * @param yMax {int} ending value on Y axis
 * @param yTickCount {int} number of ticks along Y axis
 * @param xMin {int} starting value on X axis
 * @param xMax {int} ending value on X axis
 * @param xTickCount {int} number of ticks along X axis
 * @param yLabel {string} label on Y axis
 * @param XLabel {string} label on X axis
*/
draw_axis: function (chartID, marginY, marginX, marginTopAndRight, yMin, yMax, yTickCount, xMin, xMax, xTickCount, yLabel, xLabel){
    
    if(document.getElementById(chartID) == null)
    {
        return;
    }

    var canvas = document.getElementById(chartID),
        ctx = canvas.getContext('2d');    

    ctx.save();

    var xScale = xMax-xMin;
    var yScale = yMax-yMin;

    var w = ctx.canvas.width;
    var h = ctx.canvas.height;

    var tickLength=3;
    
    var xTickValue=xScale/parseFloat(xTickCount);
    var yTickValue=yScale/parseFloat(yTickCount);

    ctx.moveTo(0,0);

    //clear screen
    ctx.strokeStyle="black";
    ctx.lineWidth=3;

    //axis
    ctx.beginPath();
    ctx.moveTo(marginY, marginTopAndRight);
    ctx.lineTo(marginY, h-marginX);
    ctx.lineTo(w-marginTopAndRight, h-marginX);
    ctx.lineWidth = 3;
    ctx.lineCap = "round";
    ctx.stroke();

    //y ticks
    ctx.beginPath();                                                               
    ctx.font="12px Georgia";
    ctx.fillStyle = "black";
    ctx.textAlign = "right";

    var tempY = h-marginX;     
    var tempYValue = yMin;

    for(var i=0;i<=yTickCount;i++)
    {                                       
        ctx.moveTo(marginY, tempY);                                   
        ctx.lineTo(marginY-5, tempY);
        ctx.fillText(tempYValue,marginY-8,tempY+4);

        tempY -= ((h-marginX-marginTopAndRight)/ (yTickCount));
        tempYValue += yTickValue;
    }

    ctx.stroke();

    //x ticks
    ctx.beginPath();                                                               
    ctx.textAlign = "center";

    var tempX = marginY;
    var tempXValue=xMin;                                
    for(var i=0;i<=xTickCount;i++)
    {                                       
        ctx.moveTo(tempX, h-marginX);                                   
        ctx.lineTo(tempX,  h-marginX+5);
        ctx.fillText(Math.round(tempXValue).toString(),tempX,h-marginX+18);

        tempX += ((w-marginY-marginTopAndRight)/ (xTickCount));
        tempXValue += xTickValue;
    }

    ctx.stroke();

    ctx.restore();

    //labels
    ctx.save();
    ctx.textAlign = "center";
    ctx.fillStyle = "DimGray";
    ctx.font="bold 14px Arial"; 

    ctx.translate(14, h/2);
    ctx.rotate(-Math.PI/2);                                                              
    ctx.fillText(yLabel,0,0);
    ctx.restore();

    ctx.save();
    ctx.textAlign = "center";
    ctx.fillStyle = "DimGray";
    ctx.font="bold 14px Georgia";
    ctx.fillText(xLabel,w/2,h-4);
    ctx.restore();                       
},


/**draw line connecting all the trades
 * @param chartID {string} dom ID name of canvas
 * @param marginY {int} margin between Y axis and vertial edge of graph
 * @param marginX {int} margin between X axis and horizontal edge of graph
 * @param marginTopAndRight {int} margin between top and rights side of canvas and grap
 * @param yMin {int} starting value on Y axis
 * @param yMax {int} ending value on Y axis
 * @param xMin {int} starting value on X axis
 * @param xMax {int} ending value on X axis
 * @param period {int} period from 1 to N of which equilibrium lines will be drawn
*/
draw_efficiency_line:function(chartID, marginY, marginX, marginTopAndRight, yMin, yMax, xMin, xMax, period)
{
    if (period == null)
        return;

    var canvas = document.getElementById(chartID),
        ctx = canvas.getContext('2d');

    var w =  ctx.canvas.width;
    var h = ctx.canvas.height;
    
    lineWidth = 3;

    ctx.save();

    ctx.strokeStyle = "dimgrey";
    ctx.lineWidth = lineWidth;
    ctx.lineCap = "round";
    ctx.font="12px Arial";
    ctx.fillStyle = "black";
    ctx.textAlign = "center";

    ctx.translate(marginY, h-marginX);

    for(i=1; i< period.trade_list.length; i++)
    {
        trade1 = period.trade_list[i-1];
        trade2 = period.trade_list[i];

        x1 = app.convertToX(i-1, xMax, xMin, w-marginY-marginTopAndRight, lineWidth);
        y1 = app.convertToY(parseFloat(trade1.trade_price), yMax, yMin, h-marginX-marginTopAndRight, lineWidth);

        x2 = app.convertToX(i, xMax, xMin, w-marginY-marginTopAndRight, lineWidth);
        y2 = app.convertToY(parseFloat(trade2.trade_price), yMax, yMin, h-marginX-marginTopAndRight, lineWidth);

        x3 = app.convertToX(i+1, xMax, xMin, w-marginY-marginTopAndRight, lineWidth);

        ctx.beginPath();
        ctx.moveTo((x1+x2)/2, y1);
        ctx.lineTo((x2+x3)/2, y2);

        ctx.stroke();
    }

    ctx.restore();
},

/**convert value to X cordinate on the graph
 * @param value {float} value to be converted to X cordinate
 * @param maxValue {float} ceiling of value on graph
 * @param minValue {float} floor of value to be shown on graph
 * @param canvasWidth {int} width of the canvas in pixels
 * @param markerWidth {int} width of the marker or line in pixels
 */
convertToX:function(value, maxValue, minValue, canvasWidth, markerWidth){
    markerWidth=0;

    tempT = canvasWidth / (maxValue-minValue);

    value-=minValue;

    if(value>maxValue) value=maxValue;

    return (tempT * value - markerWidth/2);
},

/**convert value to Y cordinate on the graph
 * @param value {float} value to be converted to Y cordinate
 * @param maxValue {float} ceiling of value on graph
 * @param minValue {float} floor of value to be shown on graph
 * @param canvasHeight {int} height of the canvas in pixels
 * @param markerHeight {int} height of the marker or line in pixels
 */
convertToY:function(value, maxValue, minValue, canvasHeight, markerHeight){
    markerHeight=0;
    
    tempT = canvasHeight / (maxValue-minValue);

    if(value > maxValue) value=maxValue;
    if(value < minValue) value=minValue;

    value-=minValue;

    if(value>maxValue) value=maxValue;

    return(-1 * tempT * value - markerHeight/2)
},
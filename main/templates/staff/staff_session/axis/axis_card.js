/**refresh the supply and demand canvas
*/
update_graph_canvas:function(){

    var el = document.getElementById('efficiency_graph');
    el.setAttribute('width', el.clientWidth);
    el.setAttribute('height', el.clientHeight);

    y_max = 1;
    x_max = app.$data.session.session_periods.length;

    var marginY=45;    //margin between left side of canvas and Y axis
    var marginX=40;    //margin between bottom of canvas and X axis
    var marginTopAndRight=10;    // margin between top and right sides of canvas and graph

    //clear canvas
    app.clear_canvas();

    //axis
    app.draw_axis("efficiency_graph", marginY, marginX, marginTopAndRight, 0, y_max, y_max, 0, x_max, x_max, "Efficiency", "Period");

    //axis
    app.draw_efficiency_line("efficiency_graph", marginY, marginX, marginTopAndRight, 0, y_max, 0, x_max);

    
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
draw_efficiency_line:function(chartID, marginY, marginX, marginTopAndRight, yMin, yMax, xMin, xMax,)
{
    
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

    ctx.beginPath();
    

    let session_period = app.$data.session.session_periods[0];

    let x1 = app.convertToX(1, xMax, xMin, w-marginY-marginTopAndRight, lineWidth);
    let y1 = app.convertToY(parseFloat(session_period.efficiency_mean), yMax, yMin, h-marginX-marginTopAndRight, lineWidth);

    ctx.moveTo(x1, y1);

    for(let i=1; i< app.$data.session.current_period; i++)
    {

        session_period = app.$data.session.session_periods[i];

        x1 = app.convertToX(i+1, xMax, xMin, w-marginY-marginTopAndRight, lineWidth);
        y1 = app.convertToY(parseFloat(session_period.efficiency_mean), yMax, yMin, h-marginX-marginTopAndRight, lineWidth);
       
        if((i+1)%7==0)
        {
            ctx.stroke();
            ctx.beginPath();
        }
        else
        {
            ctx.lineTo(x1, y1);
        }
       
    }

    ctx.stroke();

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
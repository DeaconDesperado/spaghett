window.onload = function(){

	var margin = {top: 20, right: 20, bottom: 30, left: 40},

		width = window.innerWidth - margin.left - margin.right,
		height = window.innerHeight - margin.top - margin.bottom, 

		categoryCenters = {
			left:{x:300,y:400},
			right:{x:900,y:400}
		};

        var vis = d3.select('#chart')
            .append('svg:svg')
            .attr('width',width)
            .attr('height',height);
        
        var d = null;

		function choose(choices) {
			index = Math.floor(Math.random() * choices.length);
			return choices[index];
		}

		function getRandomInt (min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        }

    function forceGraph(data){
		var d = data;

        var k = Math.sqrt(d.nodes.length / (width * height));

		d.nodes.forEach(function(nd){
			nd.cat = choose(['left','right'])
		});

        var packages = d3.set(d.nodes.map(function(nd){
            return nd.package;
        })).values().filter(function(pl){
            return pl.split('.').length <= 2;
        });

        centroids = {} 
        for(i=0;i<packages.length;i++){
            centroids[packages[i]] = {
                x:getRandomInt(0,width),
                y:getRandomInt(0,height)
            };
        }

        console.log(centroids);

        var force = d3.layout.force()
            .charge(-10/k)
            .gravity(100 * k)
            .theta(.3)
            .linkDistance(100 * k)
            .nodes(d.nodes)
            .links(d.links)
            .size([width,height])
            .start();

        var centralities = d.nodes.map(function(val,ind){
            return val.degree_cent;
        });

        var radiusScale = d3.scale.linear()
            .domain([
            		d3.min(centralities),
            		d3.max(centralities)
            ])
            .range([5,20]);

        var color = d3.scale.quantile().domain(centralities).range(['#319243', '#74c476', '#a1d99b', '#c7e9c0'].reverse());
		
		var fg = vis.append('g').attr('class','force');

        var link = fg.selectAll('line.link')
            .data(d.links)
        .enter().append('svg:line')
            .attr({
                class:'link',
                x1:function(nd){return nd.source.x},
                y1:function(nd){return nd.source.y},
                x2:function(nd){return nd.target.x},
                y2:function(nd){return nd.target.y}
            })
            .style({
                //'stroke-width':function(nd){return Math.sqrt(nd.value)}
            })

        var node = fg.selectAll('circle.node')
            .data(d.nodes)
        .enter().append('svg:circle')
            .attr({
                class:'node',
                cx:function(nd){ return nd.x},
                cy:function(nd){ return nd.y},
                r:function(nd){
                    return radiusScale(nd.degree_cent) 
                }
            })
            .style({
                fill:function(nd){return color(nd.degree_cent);}
            });
        
        node.append("svg:title")
            .text(function(nd){
                return nd.id;
            });
        

        force.on('tick',function(e){

        	//node.each(moveTowardsPackage(e));

            link.attr({
                x1:function(nd){return nd.source.x},
                y1:function(nd){return nd.source.y},
                x2:function(nd){return nd.target.x},
                y2:function(nd){return nd.target.y}
            })

            node.attr({
                cx:function(nd){ return nd.x},
                cy:function(nd){ return nd.y}
            })
        
        })

        function moveTowardsPackage(e){
			return function(d){
				var center = centroids[d.package];
				if(!center){
                   d.x += (width/2 - d.x) * 0.1;
                   d.y += (height/2 - d.y) * 0.1; 
                }else{
    				d.x+=(center.x - d.x) * 0.1;
	    			d.y+=(center.y - d.y) * 0.1;
                }
			};
		}
    };

	function drawGraph(data){
		forceGraph(data);
	}

    d3.json('graph.json',function(err,data){
    	drawGraph(data);
        
    	vis.style('opacity',1e-6)
            .transition()
            .duration(1000)
            .style('opacity',1);
    })

}

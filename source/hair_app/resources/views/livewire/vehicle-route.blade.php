<div x-data="" x-init="
        const routeData = @js($routeData);
        console.log(routeData);

        // Selecciona el contenedor del grafo
        const svg = d3.select('#graph-container')
            .append('svg')
            .attr('width', '100%')
            .attr('height', 800);

        // Define un grupo de nodos para la ruta
        const routeGroup = svg.append('g');

        // Dibuja los nodos
        routeGroup.selectAll('circle')
            .data(routeData)
            .enter()
            .append('circle')
            .attr('cx', d => d.x)
            .attr('cy', d => d.y)
            .attr('r', 5)
            .style('fill', d => d.color);
        
        //agregar texto a los nodos
        routeGroup.selectAll('text')
            .data(routeData)
            .enter()
            .append('text')
            .attr('x', d => d.x)
            .attr('y', d => d.y)
            .attr('dy', -10)
            .text(d => d.name)
            .style('fill', 'black')
            .style('font-size', '10px')
            .style('text-anchor', 'middle');

        // Dibuja las líneas entre los puntos (ruta)
        for (let i = 0; i < routeData.length - 1; i++) {
            routeGroup.append('line')
                .attr('x1', routeData[i].x)
                .attr('y1', routeData[i].y)
                .attr('x2', routeData[i + 1].x)
                .attr('y2', routeData[i + 1].y)
                .attr('stroke', 'black')
                .attr('stroke-width', 2);
        }
    ">
    <!-- Contenedor para el grafo -->
    <div id="graph-container" style="width: 100%; height: 400px;"></div>

</div>

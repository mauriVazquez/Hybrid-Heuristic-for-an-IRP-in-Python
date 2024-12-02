<div x-data="" x-init="
    const routeData = @js($routeData);

    // Configuración del contenedor
    const container = d3.select('#graph-container');
    const svg = container
        .append('svg')
        .attr('width', '100%')
        .attr('height', 800)
        .call(d3.zoom().on('zoom', (event) => {
            g.attr('transform', event.transform);
        }))
        .append('g');

    // Grupo principal
    const g = svg.append('g');

    // Cálculo inicial para centrar el grafo
    const xExtent = d3.extent(routeData, d => d.x);
    const yExtent = d3.extent(routeData, d => d.y);
    const width = container.node().getBoundingClientRect().width;
    const height = container.node().getBoundingClientRect().height;
    const scale = Math.min(
        width / (xExtent[1] - xExtent[0] + 100),
        height / (yExtent[1] - yExtent[0] + 100)
    );
    const initialTransform = d3.zoomIdentity
        .translate(width / 2, height / 2)
        .scale(scale)
        .translate(-(xExtent[1] + xExtent[0]) / 2, -(yExtent[1] + yExtent[0]) / 2);
    svg.call(d3.zoom().transform, initialTransform);

    // Fondo dinámico para light/dark mode
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    container.style('background-color', prefersDark ? '#333' : '#fff');

    // Dibuja las líneas (rutas)
    const routeGroup = g.append('g').attr('class', 'route-group');
    routeGroup.selectAll('line')
        .data(routeData.slice(0, -1))
        .enter()
        .append('line')
        .attr('x1', (d, i) => routeData[i].x)
        .attr('y1', (d, i) => routeData[i].y)
        .attr('x2', (d, i) => routeData[i + 1].x)
        .attr('y2', (d, i) => routeData[i + 1].y)
        .attr('stroke', prefersDark ? '#666' : '#999')
        .attr('stroke-width', 2)
        .style('stroke-dasharray', '4,2');

    // Dibuja los nodos
    const nodes = routeGroup.selectAll('circle')
        .data(routeData)
        .enter()
        .append('circle')
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)
        .attr('r', 8)
        .style('fill', d => d.color || (prefersDark ? '#44B5FF' : '#007BFF'))
        .on('mouseover', function (event, d) {
            d3.select(this).attr('r', 12).style('fill', '#FFD700');
        })
        .on('mouseout', function (event, d) {
            d3.select(this).attr('r', 8).style('fill', d.color || (prefersDark ? '#44B5FF' : '#007BFF'));
        })
        .append('title')
        .text(d => `Nodo: ${d.name}`);

    // Etiquetas para los nodos
    routeGroup.selectAll('text')
        .data(routeData)
        .enter()
        .append('text')
        .attr('x', d => d.x)
        .attr('y', d => d.y - 15)
        .text(d => d.name)
        .style('fill', prefersDark ? '#EEE' : '#333')
        .style('font-size', '12px')
        .style('text-anchor', 'middle');
" class="graph-container">
    <div id="graph-container" style="width: 100%; height: 400px; border: 1px solid #ddd;"></div>
</div>

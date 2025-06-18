console.log("spinner.js loaded");

document.addEventListener("DOMContentLoaded", function () {
  var padding = { top: 0, right: 0, bottom: 0, left: 100 },
    w = 400,
    h = 400,
    r = Math.min(w, h) / 2,
    rotation = 0,
    oldrotation = 0,
    picked = 100000,
    oldpick = [],
    color = d3.scale.category20();

  let currentRotation = 0;

  // Filler data — replace with your filtered restaurant list if needed
  var data = Array.from({ length: 30 }, (_, i) => ({ label: `Item ${i + 1}` }));

  var svg = d3.select("#chart")
    .append("svg")
    .data([data])
    .attr("width", w + padding.left + padding.right)
    .attr("height", h + padding.top + padding.bottom);

  var container = svg.append("g")
    .attr("class", "chartholder")
    .attr("transform", "translate(" + (w / 2 + padding.left) + "," + (h / 2 + padding.top) + ")");

  var vis = container.append("g");

  var pie = d3.layout.pie().sort(null).value(function (d) { return 1; });
  var arc = d3.svg.arc().outerRadius(r);

  var arcs = vis.selectAll("g.slice")
    .data(pie(data))
    .enter()
    .append("g")
    .attr("class", "slice");

  arcs.append("path")
    .attr("fill", function (d, i) { return color(i); })
    .attr("d", function (d) { return arc(d); });

  // Arrow indicator
  svg.append("g")
    .attr("transform", "translate(" + (w + padding.left + padding.right) + "," + ((h / 2) + padding.top) + ")")
    .append("path")
    .attr("d", "M-" + (r * .15) + ",0L0," + (r * .05) + "L0,-" + (r * .05) + "Z")
    .style("fill", "black");

  // Spin button
  container.append("circle")
    .attr("cx", 0)
    .attr("cy", 0)
    .attr("r", 60)
    .style("fill", "white")
    .style("cursor", "pointer");

  container.append("text")
    .attr("x", 0)
    .attr("y", 13)
    .attr("text-anchor", "middle")
    .text("SPIN")
    .style("font-weight", "bold")
    .style("font-size", "30px");

  container.on("click", spin);

  function spin() {
    container.on("click", null); // disable click during spin

    if (oldpick.length === data.length) {
      console.log("All options picked");
      container.on("click", null);
      return;
    }

    let ps = 720 / data.length;
    let rng = Math.floor(Math.random() * 1440 + 720);
    let newRotation = Math.round(rng / ps) * ps;
    let pickedIndex = Math.round(data.length - (newRotation % 720) / ps);
    pickedIndex = pickedIndex >= data.length ? pickedIndex % data.length : pickedIndex;
    newRotation += 180 - Math.round(ps / 2);

    oldrotation = currentRotation;
    currentRotation += newRotation;

    vis.transition()
      .duration(3000)
      .attrTween("transform", () => {
        let i = d3.interpolate("rotate(" + oldrotation + ")", "rotate(" + currentRotation + ")");
        return function (t) { return i(t); };
      })
      .each("end", function () {
        fetch('/picked-restaurant')
          .then(res => res.json())
          .then(data => {
            const chosenRestaurant = data.restaurant;
            d3.select("#question h1").text("You got: " + chosenRestaurant);
            container.on("click", spin);
          })
          .catch(() => {
            d3.select("#question h1").text("Error getting restaurant");
            container.on("click", spin);
          });
      });
  }
});

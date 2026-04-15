# UI keessatti sarara CSS keessa kan dabalame
"""
.card-header { 
    display: grid; 
    grid-template-columns: repeat(5, 1fr); 
    background: #0088cc; 
    font-weight: bold; 
    border-radius: 5px 5px 0 0;
    font-size: 0.8rem;
    padding: 2px 0;
}
"""

# JavaScript loojika haaraa (Mata-duree kaartellaa)
"""
function startLiveGame() {
    // ... (Koodii kee inni duraa) ...
    myTickets.forEach(id => {
        const div = document.createElement('div'); div.className = 'card';
        // Mata-duree B-I-N-G-O asitti dabalame
        div.innerHTML = `
            <div class="card-header">
                <div>B</div><div>I</div><div>N</div><div>G</div><div>O</div>
            </div>
            <div class="b-grid" id="g-${id}"></div>
            <div style="font-size:0.6rem; margin-top:2px;">#${id}</div>`;
        document.getElementById('my-cards-ui').appendChild(div);
        
        // ... (Lakkofsota kaartellaa keessatti guutuu) ...
    });
}
"""

<!DOCTYPE html>
<html lang="om">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bingo Ethiopia - Pro</title>
    <style>
        body { background: #011627; color: white; text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; }
        .header { background: #0b1c2c; padding: 20px; border-bottom: 3px solid #ff9f1c; }
        .balance-text { font-size: 28px; color: #2ec4b6; font-weight: bold; }
        .section-title { margin-top: 20px; font-size: 18px; color: #fdfffc; }
        .btn-group { display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; padding: 10px; }
        .btn { padding: 15px 25px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 14px; transition: 0.3s; min-width: 100px; }
        .telebirr { background: #00a8ff; color: white; }
        .cbe-birr { background: #9c27b0; color: white; }
        .cbe { background: #ffc107; color: black; }
        .btn:hover { opacity: 0.8; transform: scale(1.05); }
        .ticket-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; padding: 20px; }
        .ticket { background: #1b262c; border: 1px solid #3282b8; padding: 15px; border-radius: 12px; cursor: pointer; }
        .selected { border: 2px solid #00ff00; background: #0f4c75; box-shadow: 0 0 10px #00ff00; }
    </style>
</head>
<body>

<div class="header">
    <div class="section-title">HERREGA KEESSAN (WALLET)</div>
    <div class="balance-text"><span id="wallet-bal">500.00</span> ETB</div>
</div>

<div class="section-title">DEPOSIT (MAALLAQA GALCHII)</div>
<div class="btn-group">
    <button class="btn telebirr" onclick="handleAction('Telebirr', 'deposit')">Telebirr</button>
    <button class="btn cbe-birr" onclick="handleAction('CBE_Birr', 'deposit')">CBE Birr</button>
    <button class="btn cbe" onclick="handleAction('CBE', 'deposit')">CBE Bank</button>
</div>

<div class="section-title">WITHDRAW (MAALLAQA BAASII)</div>
<div class="btn-group">
    <button class="btn telebirr" onclick="handleAction('Telebirr', 'withdraw')">Telebirr</button>
    <button class="btn cbe-birr" onclick="handleAction('CBE_Birr', 'withdraw')">CBE Birr</button>
    <button class="btn cbe" onclick="handleAction('CBE', 'withdraw')">CBE Bank</button>
</div>

<hr style="border: 0.5px solid #333; margin: 20px 0;">

<div class="section-title">TIKKEETII FILADHU (10 ETB)</div>
<div class="ticket-container" id="tickets">
    <div class="ticket" onclick="toggleTicket(this)">Ticket #1</div>
    <div class="ticket" onclick="toggleTicket(this)">Ticket #2</div>
    <div class="ticket" onclick="toggleTicket(this)">Ticket #3</div>
    <div class="ticket" onclick="toggleTicket(this)">Ticket #4</div>
</div>

<script>
    let currentBalance = 500.00;

    function toggleTicket(el) {
        if (currentBalance >= 10) {
            if (!el.classList.contains('selected')) {
                currentBalance -= 10;
                el.classList.add('selected');
                document.getElementById('wallet-bal').innerText = currentBalance.toFixed(2);
                alert("Tikkeetiin filatameera!");
            }
        } else {
            alert("Maaloo dura Deposit godhaa! Balance keessan gahaa miti.");
        }
    }

    function handleAction(provider, type) {
        let amount = prompt(`Hamma ${type} gochuu barbaaddan barreessaa (${provider}):`);
        
        if (amount && !isNaN(amount)) {
            if (type === 'deposit') {
                alert(`${provider} kallaattiin isiniif banamaa jira...`);
                // Kallaattiin gara linkii kaffaltii deema
                window.location.href = "https://payment-gateway.et/pay?method=" + provider;
            } else {
                // Barreeffamni 'Admin qunnamaa' jedhu asitti dhabameera
                alert(`Gaffiin baasii ${amount} ETB karaa ${provider} fudhatameera. Sa'aatii 24 keessatti herrega keessan irratti ni dhangala'a.`);
            }
        }
    }
</script>

</body>
</html>

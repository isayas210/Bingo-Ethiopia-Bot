<!DOCTYPE html>
<html lang="om">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bingo Ethiopia Bot</title>
    <style>
        body { background: #011627; color: white; text-align: center; font-family: sans-serif; margin: 0; padding: 0; }
        .header { background: #0b1c2c; padding: 20px; border-bottom: 3px solid gold; }
        .wallet-bal { font-size: 30px; color: #2ec4b6; font-weight: bold; }
        .btn-container { display: flex; justify-content: center; gap: 10px; padding: 15px; flex-wrap: wrap; }
        .btn { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; min-width: 100px; }
        .telebirr { background: #0088cc; color: white; }
        .cbe-birr { background: #800080; color: white; }
        .cbe { background: #ffcc00; color: black; }
        .ticket-area { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 20px; }
        .ticket { background: #1b262c; border: 1px solid #333; padding: 20px; border-radius: 12px; cursor: pointer; }
        .selected { border: 2px solid #00ff00; background: #0d2a44; box-shadow: 0 0 10px #00ff00; }
    </style>
</head>
<body>

<div class="header">
    <div>BALANCE KEESSAN</div>
    <div class="wallet-bal"><span id="display-bal">500.00</span> ETB</div>
</div>

<p>MAALLAQA GALCHII (DEPOSIT)</p>
<div class="btn-container">
    <button class="btn telebirr" onclick="doAction('Telebirr', 'deposit')">Telebirr</button>
    <button class="btn cbe-birr" onclick="doAction('CBE_Birr', 'deposit')">CBE Birr</button>
    <button class="btn cbe" onclick="doAction('CBE', 'deposit')">CBE Bank</button>
</div>

<p>MAALLAQA BAASII (WITHDRAW)</p>
<div class="btn-container">
    <button class="btn telebirr" onclick="doAction('Telebirr', 'withdraw')">Telebirr</button>
    <button class="btn cbe-birr" onclick="doAction('CBE_Birr', 'withdraw')">CBE Birr</button>
    <button class="btn cbe" onclick="doAction('CBE', 'withdraw')">CBE Bank</button>
</div>

<hr style="border: 0.1px solid #333;">

<div class="ticket-area">
    <div class="ticket" onclick="buyTicket(this, 1)">Ticket #1<br>10 ETB</div>
    <div class="ticket" onclick="buyTicket(this, 2)">Ticket #2<br>10 ETB</div>
    <div class="ticket" onclick="buyTicket(this, 3)">Ticket #3<br>10 ETB</div>
    <div class="ticket" onclick="buyTicket(this, 4)">Ticket #4<br>10 ETB</div>
</div>

<script>
    let myBalance = 500.00;

    function buyTicket(el, id) {
        if (myBalance >= 10) {
            myBalance -= 10;
            document.getElementById('display-bal').innerText = myBalance.toFixed(2);
            el.classList.add('selected');
            alert("Tikkeetii #" + id + " milkaaa'inaan filattaniittu!");
        } else {
            alert("Maaloo dura Deposit godhaa!");
        }
    }

    async function doAction(provider, type) {
        let amt = prompt(`Hamma ${type} gochuu barbaaddan (${provider}):`);
        if (!amt || isNaN(amt)) return;

        const res = await fetch('/api/payment', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({method: provider, amount: amt, action: type})
        });
        const data = await res.json();

        if (type === 'deposit') {
            alert(data.msg);
            window.location.href = data.url;
        } else {
            alert(data.msg);
        }
    }
</script>
</body>
</html>

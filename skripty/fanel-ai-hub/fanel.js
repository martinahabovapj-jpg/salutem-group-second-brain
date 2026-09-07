    <script>
        // ===================== FANEL =====================
        (function () {
            var el = document.getElementById('fn-data');
            if (!el) return;
            var FN = JSON.parse(el.textContent);
            var IT = FN.items;

            function esc(s) {
                return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
                    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
                });
            }
            function byId(id) { return document.getElementById(id); }
            function cnt(pred) { var n = 0; IT.forEach(function (i) { if (pred(i)) n++; }); return n; }
            function label(list, key) {
                var out = key;
                list.forEach(function (x) { if (x.key === key) out = x.nazev; });
                return out;
            }
            function sklon(n, a, b, c) { return n === 1 ? a : (n >= 2 && n <= 4 ? b : c); }

            var FAZE = FN.faze, BCL = FN.bc_popisky, BLL = FN.blok_popisky;
            var FKEY = FAZE.map(function (f) { return f.key; });

            // ---- zásobník bolestí ----
            (function () {
                var h = '';
                FN.zasobnik.forEach(function (z) {
                    h += '<div class="fn-res-c ' + esc(z.key) + '">'
                       + '<div class="n">' + z.pocet + ' <small>' + sklon(z.pocet, 'bolest', 'bolesti', 'bolestí') + ' · ' + z.hodin + ' h/týdně</small></div>'
                       + '<h4>' + esc(z.nazev) + '</h4><p>' + esc(z.popis) + '</p></div>';
                });
                byId('fn-zasobnik').innerHTML = h;
            })();

            // ---- sloupcový graf fází ----
            var aktivni = null;
            function renderBars() {
                var max = 1;
                FAZE.forEach(function (f) { if (f.pocet > max) max = f.pocet; });
                var h = '';
                FAZE.forEach(function (f) {
                    var w = f.pocet ? Math.max(2, Math.round(f.pocet / max * 100)) : 0;
                    h += '<button type="button" class="fn-bar f-' + esc(f.key) + (f.pocet ? '' : ' fn-bar-empty') + '"'
                       + ' aria-pressed="' + (aktivni === f.key ? 'true' : 'false') + '"'
                       + ' data-f="' + esc(f.key) + '" title="' + esc(f.popis) + '">'
                       + '<span class="fn-bar-l">' + esc(f.nazev) + '</span>'
                       + '<span class="fn-bar-t"><span class="fn-bar-f" style="width:' + w + '%"></span></span>'
                       + '<span class="fn-bar-n">' + f.pocet + '</span></button>';
                });
                byId('fn-bars').innerHTML = h;
                byId('fn-bars').querySelectorAll('.fn-bar').forEach(function (b) {
                    b.addEventListener('click', function () {
                        var k = b.getAttribute('data-f');
                        aktivni = (aktivni === k) ? null : k;
                        renderBars(); renderChips(); renderTbl();
                        byId('fn-tbl').scrollIntoView({ behavior: 'smooth', block: 'center' });
                    });
                });
            }

            // ---- kritéria fází ----
            (function () {
                var h = '<table class="pm"><thead><tr><th style="width:210px">Fáze</th>'
                      + '<th class="num">počet</th><th>Kdy tam zadání patří</th></tr></thead><tbody>';
                FAZE.forEach(function (f) {
                    h += '<tr><td><strong>' + esc(f.nazev) + '</strong></td>'
                       + '<td class="num">' + (f.pocet ? '<strong>' + f.pocet + '</strong>' : '<span style="color:var(--gray-400)">0</span>') + '</td>'
                       + '<td>' + esc(f.popis) + '</td></tr>';
                });
                h += '</tbody></table>';
                byId('fn-krit').innerHTML = h;
            })();

            // ---- klíčová čísla ----
            (function () {
                var celkem = IT.length;
                var sZadanim = cnt(function (i) { return i.zadani; });
                var bcPlny = cnt(function (i) { return i.bc === 'plny'; });
                var realizace = cnt(function (i) { return i.faze === 'realizace'; });
                var realBezBc = cnt(function (i) { return i.faze === 'realizace' && i.bc !== 'plny'; });
                var h = '';
                h += '<div class="fn-kpi"><div class="fn-kpi-v">' + celkem + '</div><div class="fn-kpi-l">zadání je dnes ve fanelu. ' + sZadanim + ' z nich má ve Freelu sepsané zadání, u zbytku je zatím jen název</div></div>';
                h += '<div class="fn-kpi ' + (bcPlny > 1 ? '' : 'bad') + '"><div class="fn-kpi-v">' + bcPlny + '</div><div class="fn-kpi-l">' + sklon(bcPlny, 'zadání má', 'zadání mají', 'zadání má') + ' vyčíslený přínos v Kč za rok. Bez čísla se nedá prioritizovat</div></div>';
                h += '<div class="fn-kpi ' + (realBezBc ? 'bad' : '') + '"><div class="fn-kpi-v">' + realBezBc + ' z ' + realizace + '</div><div class="fn-kpi-l">věcí, které se právě staví, nemá vyčíslený přínos</div></div>';
                var nezapsano = cnt(function (i) { return i.blok === 'nezapsano'; });
                h += '<div class="fn-kpi warn"><div class="fn-kpi-v">' + nezapsano + '</div><div class="fn-kpi-l">' + sklon(nezapsano, 'zadání nemá', 'zadání nemají', 'zadání nemá') + ' zapsané, čí je další krok</div></div>';
                byId('fn-kpis').innerHTML = h;

                byId('fn-bars-note').innerHTML = 'Stav k ' + esc(FN.aktualizovano)
                    + '. Zdroj: ' + esc(FN.zdroj)
                    + '. Fáze <em>Business case</em> a <em>Vyhodnoceno</em> jsou prázdné proto, že dnes nejsou samostatným stavem ve Freelu — nacenění se děje uvnitř jiných fází a přeměření po nasazení se ještě nedělalo.';
            })();

            // ---- kříž fáze × business case ----
            (function () {
                var h = '<table class="pm"><thead><tr><th>Fáze</th>';
                BCL.forEach(function (b) { h += '<th class="num">' + esc(b.nazev) + '</th>'; });
                h += '<th class="num">celkem</th></tr></thead><tbody>';
                FAZE.forEach(function (f) {
                    if (!f.pocet) return;
                    h += '<tr><td><strong>' + esc(f.nazev) + '</strong></td>';
                    BCL.forEach(function (b) {
                        var n = cnt(function (i) { return i.faze === f.key && i.bc === b.key; });
                        h += '<td class="num">' + (n ? '<span class="tag fn-bc-' + esc(b.key) + '">' + n + '</span>' : '—') + '</td>';
                    });
                    h += '<td class="num"><strong>' + f.pocet + '</strong></td></tr>';
                });
                h += '<tr><td><strong>Celkem</strong></td>';
                BCL.forEach(function (b) {
                    h += '<td class="num"><strong>' + cnt(function (i) { return i.bc === b.key; }) + '</strong></td>';
                });
                h += '<td class="num"><strong>' + IT.length + '</strong></td></tr>';
                h += '</tbody></table>';
                byId('fn-bc').innerHTML = h;
            })();

            // ---- na čem to stojí ----
            (function () {
                var h = '<table class="pm"><thead><tr><th style="width:250px">Na čem to stojí</th><th class="num">počet</th><th>Konkrétně u kterých zadání</th></tr></thead><tbody>';
                BLL.forEach(function (b) {
                    var rs = IT.filter(function (i) { return i.blok === b.key; });
                    if (!rs.length) return;
                    h += '<tr><td><span class="tag fn-bl-' + esc(b.key) + '">' + esc(b.nazev) + '</span></td>'
                       + '<td class="num"><strong>' + rs.length + '</strong></td><td>';
                    rs.forEach(function (r) {
                        h += '<div style="margin-bottom:6px"><strong>' + esc(r.nazev) + '</strong>'
                           + '<span class="fn-cell-sub">' + esc(r.blok_text) + '</span></div>';
                    });
                    h += '</td></tr>';
                });
                h += '</tbody></table>';
                byId('fn-blok').innerHTML = h;
            })();

            // ---- filtrační chipy ----
            function renderChips() {
                var box = byId('fn-chips');
                var h = '<label>Fáze</label>';
                h += '<button type="button" class="fn-chip" data-f="" aria-pressed="' + (aktivni === null ? 'true' : 'false') + '">vše</button>';
                FAZE.forEach(function (f) {
                    if (!f.pocet) return;
                    h += '<button type="button" class="fn-chip" data-f="' + esc(f.key) + '" aria-pressed="'
                       + (aktivni === f.key ? 'true' : 'false') + '">' + esc(f.nazev) + ' (' + f.pocet + ')</button>';
                });
                h += '<span class="fn-count" id="fn-tbl-count"></span>';
                box.innerHTML = h;
                box.querySelectorAll('.fn-chip').forEach(function (b) {
                    b.addEventListener('click', function () {
                        var k = b.getAttribute('data-f');
                        aktivni = k === '' ? null : k;
                        renderBars(); renderChips(); renderTbl();
                    });
                });
            }

            // ---- tabulka zadání ----
            function renderTbl() {
                var rs = IT.filter(function (i) { return aktivni === null || i.faze === aktivni; });
                rs = rs.slice().sort(function (a, b) {
                    var d = FKEY.indexOf(a.faze) - FKEY.indexOf(b.faze);
                    return d !== 0 ? d : a.nazev.localeCompare(b.nazev, 'cs');
                });
                var h = '';
                rs.forEach(function (r) {
                    var bcTxt = r.prinos ? r.prinos
                        : [r.hodiny ? 'hodiny: ' + r.hodiny : '', r.investice ? 'investice: ' + r.investice : ''].filter(Boolean).join(' · ');
                    h += '<tr>'
                       + '<td>' + esc(label(FAZE, r.faze)) + (r.dve_stitky ? ' <span class="tag fn-bc-zadny" title="Úkol má dva štítky pipeline naráz">2 štítky</span>' : '') + '</td>'
                       + '<td><strong>' + esc(r.nazev) + '</strong>'
                       + (r.dalsi_krok ? '<span class="fn-cell-sub">Další krok: ' + esc(r.dalsi_krok) + '</span>' : '')
                       + (r.v_provozu_od ? '<span class="fn-cell-sub">V provozu od ' + esc(r.v_provozu_od) + '</span>' : '')
                       + '</td>'
                       + '<td style="color:var(--gray-500);font-size:.85rem">' + esc(r.vetev) + '</td>'
                       + '<td style="font-size:.85rem">' + (r.zadavatel ? esc(r.zadavatel) : '<span style="color:var(--gray-400)">nezapsán</span>') + '</td>'
                       + '<td><span class="tag fn-bc-' + esc(r.bc) + '">' + esc(label(BCL, r.bc)) + '</span>'
                       + (bcTxt ? '<span class="fn-cell-sub">' + esc(bcTxt.slice(0, 110)) + (bcTxt.length > 110 ? '…' : '') + '</span>' : '')
                       + '</td>'
                       + '<td><span class="tag fn-bl-' + esc(r.blok) + '">' + esc(label(BLL, r.blok)) + '</span>'
                       + '<span class="fn-cell-sub">' + esc(r.blok_text) + '</span></td>'
                       + '</tr>';
                });
                byId('fn-tbody').innerHTML = h;
                var c = byId('fn-tbl-count');
                if (c) c.textContent = rs.length + ' z ' + IT.length;
            }

            // ---- hranice fanelu ----
            (function () {
                var bez = cnt(function (i) { return i.faze === 'bez_stavu'; });
                var dve = cnt(function (i) { return i.dve_stitky; });
                var park = cnt(function (i) { return i.faze === 'parkoviste'; });
                var h = '<strong>Co fanel dnes neumí a proč.</strong><br>';
                h += '<strong>1. Nemá čas.</strong> Ukazuje snímek, ne jak se fronta vyprazdňuje. Časová osa přijde, až bude víc než jeden snímek — dřív by to byla čára mezi dvěma body.<br>';
                h += '<strong>2. Nerozliší „schváleno k realizaci" od „staví se".</strong> Ve Freelu je na obojí jeden štítek <em>in process</em>. Kdo to chce vidět odděleně, musí přidat štítek — fanel to pak ukáže sám.<br>';
                h += '<strong>3. ' + bez + ' ' + sklon(bez, 'zadání nemá', 'zadání nemají', 'zadání nemá') + ' štítek pipeline</strong>, takže je fanel neumí zařadit a drží je ve sloupci Bez stavu. ';
                h += dve ? 'Další ' + dve + ' ' + sklon(dve, 'má', 'mají', 'má') + ' štítky dva naráz, což pravidlo „právě jeden štítek" zakazuje; fanel je řadí podle toho pozdějšího a označuje je v tabulce.<br>' : '<br>';
                h += '<strong>4. Parkoviště není fáze, je to nerozhodnuto.</strong> ' + park + ' ' + sklon(park, 'zadání tam leží', 'zadání tam leží', 'zadání tam leží') + ' bez ano i bez ne. Ve fanelu to visí na kraji záměrně, aby to nezapadlo.<br>';
                h += '<strong>5. Business case v Kč má ' + cnt(function (i) { return i.bc === 'plny'; }) + ' zadání ze ' + IT.length + '.</strong> Ne proto, že by čísla nešla spočítat, ale proto, že se do Freela nedopsala. Dokud tam nebudou, je prioritizace věc dojmu.';
                byId('fn-hranice').innerHTML = h;
            })();

            renderBars(); renderChips(); renderTbl();
        })();
    </script>

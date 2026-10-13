from pathlib import Path
import shutil,difflib
src=Path('original');dst=Path('patched')
shutil.copytree(src,dst,dirs_exist_ok=True)
p=dst/'influence/index.html';s=p.read_text(encoding='utf-8')
s=s.replace('Math.sqrt(r.se * r.se + loo.tau2);','Math.sqrt(hat * (r.se * r.se + loo.tau2));')
s=s.replace('const covRatio = (loo.seMu / full.seMu) ** 2;','''const covRatio = (loo.seMu / full.seMu) ** 2;
          // DFBETAS uses the full design evaluated at the deleted tau-squared.
          const dfbeta = (full.mu - loo.mu) * Math.sqrt(rows.reduce((s, x) => s + 1 / (x.se * x.se + loo.tau2), 0));
          const influential = Math.abs(dffits) > 3 / Math.sqrt(k - 1) ||
            cooksD > 0.4549364231195727 || hat > 3 / k || Math.abs(dfbeta) > 1;''')
s=s.replace('...r, hat, resid, dffits, cooksD, covRatio,','...r, hat, resid, dffits, cooksD, covRatio, influential,')
s=s.replace('d.cooksD > 1 || d.hat > hatThreshold || Math.abs(d.resid) > 2','d.influential')
s=s.replace('d.cooksD > 1 || d.hat > 3 / diag.length || Math.abs(d.resid) > 2','d.influential')
s=s.replace('AlmDiagPlots.baujat(rows.map(r => r.te), rows.map(r => r.se * r.se))','AlmDiagPlots.baujat(rows.map(r => r.te), rows.map(r => r.se * r.se), "REML")')
s=s.replace('Horizontal: each study\'s contribution to heterogeneity (Q);','Horizontal: each study\'s squared Pearson residual from the REML model;')
s=s.replace('Contribution to Q (heterogeneity)','Squared Pearson residual (REML)')
s=s.replace('${Y(1)}','${Y(0.4549364231195727)}')
start=s.index('Flags in red:');end=s.index(' Matches metafor::influence()',start)
s=s[:start]+"Flags in red: |DFFITS| &gt; 3/√(k−1), Cook's D &gt; median χ²(1), hat &gt; 3/k, or |DFBETAS| &gt; 1."+s[end:]
p.write_text(s,encoding='utf-8',newline='\n')
p=dst/'shared/diagnostic-plots.js';s=p.read_text(encoding='utf-8')
s=s.replace('function baujat(yi, vi) {\n    var k = yi.length, fit = _dl(yi, vi),','''function baujat(yi, vi, method) {
    function fitModel(y, v) {
      if (!method || method === "DL") return _dl(y, v);
      var p = global.AlmMaCore.pool(y, v, { method: method });
      return { mu: p.mu, se: p.se, tau2: p.tau2 };
    }
    var k = yi.length, fit = fitModel(yi, vi),''')
s=s.replace('var f2 = _dl(yLoo, vLoo);','var f2 = fitModel(yLoo, vLoo);')
p.write_text(s,encoding='utf-8',newline='\n')
diff=[]
for rel in ['influence/index.html','shared/diagnostic-plots.js']:
 diff.extend(difflib.unified_diff((src/rel).read_text(encoding='utf-8').splitlines(True),(dst/rel).read_text(encoding='utf-8').splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
Path('fix.patch').write_text(''.join(diff),encoding='utf-8',newline='\n')

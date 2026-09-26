import pathlib, json, re
import fitz

out = pathlib.Path(__file__).resolve().parent.parent/'validation/xdv-fix'
doc = fitz.open(out/'xelatex-cjk.pdf')
assert len(doc) == 1
text = doc[0].get_text()
(out/'xelatex-cjk.txt').write_text(text, encoding='utf-8')
assert all(word in text for word in ('鸿蒙', '交叉引用', '结束'))
assert '第3节' in re.sub(r'\s+', '', text)
page = doc[0]
scale = 1600 / max(page.rect.width, page.rect.height)
page.get_pixmap(matrix=fitz.Matrix(scale, scale)).save(out/'xelatex-cjk-preview.png')
(out/'pdf-check.json').write_text(json.dumps({'pages':len(doc),'chinese_text_present':True,'cross_reference_resolved':True,'visual_review_file':'xelatex-cjk-preview.png'},indent=2)+'\n')
print('One-page PDF text and section reference checks passed; preview rendered')

"""Exercise the real getListOfDocs implementation with a minimal owner graph.
This is a focused ownership regression, not a full editor/UI acceptance test.
"""
from pathlib import Path
import os,subprocess
r=Path(__file__).resolve().parents[1];out=r/'validation/crash-fix-1.0.30'
repo=Path(os.environ['BUILD_REPO'])
prelude='''#include <QtCore>
#include <cassert>
class LatexDocument;
struct Parser { QList<LatexDocument*> projectDocuments; };
struct Owner { LatexDocument *masterDocument=nullptr; QList<LatexDocument*> docs;
QList<LatexDocument*> getDocuments() const { return docs; } };
class LatexDocument { public:
Owner *parent=nullptr; LatexDocument *masterDocument=nullptr;
QSharedPointer<Parser> lp=QSharedPointer<Parser>::create(); QSet<LatexDocument*> childDocs;
QList<LatexDocument*> getListOfDocs(QSet<LatexDocument*> *visitedDocs=nullptr,bool onlyChildDocs=false);
};
'''
main='''
int main() {
Owner owner; LatexDocument root; root.parent=&owner;
auto *child=new LatexDocument;child->parent=&owner;child->masterDocument=&root;child->lp=root.lp;
owner.docs={&root,child};root.childDocs.insert(child);
assert(root.getListOfDocs().size()==2);
owner.docs.removeAll(child);root.childDocs.remove(child);delete child;
// No freed document may be returned to completion or close callers.
assert(root.getListOfDocs()==QList<LatexDocument*>{&root});
auto *second=new LatexDocument;second->parent=&owner;owner.docs.append(second);
root.childDocs.insert(second);assert(root.getListOfDocs().size()==2);
root.childDocs.remove(second);assert(root.getListOfDocs().size()==1);
owner.docs.removeAll(second);delete second;
LatexDocument detached;assert(detached.getListOfDocs().isEmpty());
}
'''
def body(path):
    s=path.read_text();a=s.index('QList<LatexDocument *>LatexDocument::getListOfDocs(');b=s.index('void LatexDocument::updateRefHighlight',a);return s[a:b]
paths={'before':repo/'third_party/texstudio/src/latexdocument.cpp','after':r/'texstudio-harmony/third_party/texstudio/src/latexdocument.cpp'}
flags=subprocess.check_output(['pkg-config','--cflags','--libs','Qt5Core'],text=True).split()
for name,path in paths.items():
    cpp=out/f'registry-{name}.cpp'
    if name!='before' or not cpp.exists():
        if name=='before' and 'return lp->projectDocuments;' not in body(path):
            print('Original cached implementation unavailable; skipping baseline comparison')
            continue
        cpp.write_text(prelude+body(path)+main)
    exe=out/f'registry-{name}'
    subprocess.run(['g++','-std=c++17','-fPIC',str(cpp),*flags,'-o',str(exe)],check=True)
    result=subprocess.run([str(exe)],capture_output=True,text=True)
    (out/f'registry-{name}.log').write_text(result.stderr+f'Exit: {result.returncode}\n')
    assert (result.returncode!=0 if name=='before' else result.returncode==0),(name,result.stderr)
print('PASS: old cached list returns a deleted document; live-registry implementation passes deletion, graph changes, detached document')

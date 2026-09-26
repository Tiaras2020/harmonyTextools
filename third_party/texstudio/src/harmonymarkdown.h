#ifndef HARMONY_MARKDOWN_H
#define HARMONY_MARKDOWN_H
#include <QtCore>
// Qt 5.12 has no QTextDocument::setMarkdown. Emit the supported rich-text
// subset explicitly; raw HTML and image loads are deliberately not evaluated.
namespace HarmonyMarkdown {
inline QString inlineText(const QString &text,int depth=0) {
    if(depth>10)return text.toHtmlEscaped();
    QString out;
    for(int i=0;i<text.size();) {
        if(text[i]=='\\' && i+1<text.size() && QStringLiteral("\\`*_{}[]()#+-.!>|~").contains(text[i+1])) {out+=QString(text[i+1]).toHtmlEscaped();i+=2;continue;}
        if(text[i]=='`') {
            int n=1;while(i+n<text.size() && text[i+n]=='`')++n;
            QString mark(n,'`');int end=text.indexOf(mark,i+n);
            if(end>=0){out+="<code>"+text.mid(i+n,end-i-n).toHtmlEscaped()+"</code>";i=end+n;continue;}
        }
        if(text[i]=='[' || (text[i]=='!' && i+1<text.size() && text[i+1]=='[')) {
            bool image=text[i]=='!';int start=i+(image?2:1),end=text.indexOf("](",start);
            if(end>=0){int stop=text.indexOf(')',end+2);if(stop>=0){QString label=inlineText(text.mid(start,end-start),depth+1);QString url=text.mid(end+2,stop-end-2).trimmed();QUrl parsed(url);
                if(!image && QStringList{"https","http","mailto"}.contains(parsed.scheme().toLower()))out+="<a href=\""+url.toHtmlEscaped()+"\">"+label+"</a>";
                else out+=label;
                i=stop+1;continue;}}
        }
        bool formatted=false;
        for(const QString &mark:QStringList{"***","___","**","__","~~","*","_"}) {
            if(text.midRef(i,mark.size())!=mark)continue;
            if(mark.contains('_') && i>0 && text[i-1].isLetterOrNumber())continue;
            int end=text.indexOf(mark,i+mark.size());if(end<=i+mark.size())continue;
            if(text[i+mark.size()].isSpace() || text[end-1].isSpace())continue;
            QString tag=mark.size()==3?"b><i":mark.size()==2?(mark=="~~"?"s":"b"):"i";
            QString close=mark.size()==3?"i></b":tag;
            out+="<"+tag+">"+inlineText(text.mid(i+mark.size(),end-i-mark.size()),depth+1)+"</"+close+">";i=end+mark.size();formatted=true;break;
        }
        if(formatted)continue;
        out+=QString(text[i++]).toHtmlEscaped();
    }
    return out;
}
inline QStringList cells(QString line) {
    line=line.trimmed();if(line.startsWith('|'))line.remove(0,1);if(line.endsWith('|') && !line.endsWith("\\|"))line.chop(1);
    QStringList result;QString cell;bool escaped=false,code=false;
    for(QChar c:line){if(c=='|' && !escaped && !code){result<<cell.trimmed();cell.clear();}else cell+=c;if(c=='`' && !escaped)code=!code;if(c=='\\' && !escaped)escaped=true;else escaped=false;}
    result<<cell.trimmed();return result;
}
inline bool divider(const QString &line) {
    const auto columns=cells(line);if(columns.isEmpty())return false;
    for(const auto &c:columns)if(!QRegularExpression("^:?-{3,}:?$").match(c).hasMatch())return false;
    return true;
}
inline QString render(QString text,int depth=0) {
    if(depth>10)return "<p>"+inlineText(text)+"</p>";
    text.replace("\r\n","\n");const auto lines=text.split('\n');QString out,paragraph;
    struct List {QString tag;int indent;};QVector<List> lists;
    auto flush=[&]{if(!paragraph.isEmpty()){out+="<p>"+paragraph+"</p>";paragraph.clear();}};
    auto closeLists=[&]{while(!lists.isEmpty()){out+="</li></"+lists.takeLast().tag+">";}};
    const QRegularExpression fence("^\\s{0,3}(`{3,}|~{3,})(.*)$"),heading("^\\s{0,3}(#{1,6})\\s+(.+)$"),list("^(\\s*)([-+*]|\\d+[.)])\\s+(.+)$");
    for(int i=0;i<lines.size();++i) {
        QString line=lines[i],trim=line.trimmed();auto f=fence.match(line);
        if(f.hasMatch()) {flush();closeLists();QString mark=f.captured(1),code;bool first=true;
            while(++i<lines.size()){QString end=lines[i].trimmed();if(end.size()>=mark.size() && end==QString(end.size(),mark[0]))break;if(!first)code+='\n';first=false;code+=lines[i];}
            out+="<pre style='background-color:#f2f5f9;margin-top:4px;margin-bottom:4px;'>"+code.toHtmlEscaped()+"</pre>";continue;
        }
        if(trim.isEmpty()){flush();closeLists();continue;}
        auto h=heading.match(line);
        if(h.hasMatch()){flush();closeLists();int level=h.captured(1).size();out+=QString("<h%1>").arg(level)+inlineText(h.captured(2))+QString("</h%1>").arg(level);continue;}
        if(i+1<lines.size() && QRegularExpression("^\\s*(={3,}|-{3,})\\s*$").match(lines[i+1]).hasMatch()) {flush();closeLists();QString tag=lines[++i].trimmed().startsWith('=')?"h1":"h2";out+="<"+tag+">"+inlineText(line)+"</"+tag+">";continue;}
        if(QRegularExpression("^\\s{0,3}([-*_])(?:\\s*\\1){2,}\\s*$").match(line).hasMatch()){flush();closeLists();out+="<hr>";continue;}
        if(trim.startsWith('>')){flush();closeLists();QString quote;while(i<lines.size() && lines[i].trimmed().startsWith('>')){QString q=lines[i].trimmed().mid(1);if(q.startsWith(' '))q.remove(0,1);quote+=q+'\n';++i;}--i;out+="<blockquote>"+render(quote,depth+1)+"</blockquote>";continue;}
        if(i+1<lines.size() && line.contains('|') && divider(lines[i+1])) {
            flush();closeLists();auto heads=cells(line),alignment=cells(lines[++i]);out+="<table border='1' cellspacing='0' cellpadding='4' width='100%'><tr>";
            for(auto c:heads)out+="<th bgcolor='#edf1f5'>"+inlineText(c)+"</th>";out+="</tr>";
            while(i+1<lines.size() && lines[i+1].contains('|') && !lines[i+1].trimmed().isEmpty()){auto row=cells(lines[++i]);out+="<tr>";for(int col=0;col<heads.size();++col){QString a=alignment.value(col);QString align=a.endsWith(':')?(a.startsWith(':')?"center":"right"):"left";out+="<td align='"+align+"'>"+inlineText(row.value(col))+"</td>";}out+="</tr>";}
            out+="</table>";continue;
        }
        auto item=list.match(line);
        if(item.hasMatch()) {
            flush();int indent=item.captured(1).size();QString tag=item.captured(2)[0].isDigit()?"ol":"ul";
            while(!lists.isEmpty() && indent<lists.last().indent)out+="</li></"+lists.takeLast().tag+">";
            if(!lists.isEmpty() && indent==lists.last().indent && tag!=lists.last().tag)out+="</li></"+lists.takeLast().tag+">";
            if(lists.isEmpty() || indent>lists.last().indent){out+="<"+tag+"><li>";lists.append({tag,indent});}else out+="</li><li>";
            QString body=item.captured(3);if(body.startsWith("[ ] "))body=QStringLiteral("☐ ")+body.mid(4);else if(body.startsWith("[x] ",Qt::CaseInsensitive))body=QStringLiteral("☑ ")+body.mid(4);
            out+=inlineText(body);continue;
        }
        if(!lists.isEmpty() && line.size()-line.trimmed().size()>lists.last().indent){out+="<br>"+inlineText(trim);continue;}
        closeLists();if(!paragraph.isEmpty())paragraph+="<br>";paragraph+=inlineText(line);
    }
    flush();closeLists();return out;
}
}
#endif

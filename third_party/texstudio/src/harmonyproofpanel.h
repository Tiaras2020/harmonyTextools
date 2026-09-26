#ifndef HARMONY_PROOF_PANEL_H
#define HARMONY_PROOF_PANEL_H
#include "harmonyproofread.h"
#include "harmonyfloatingpanel.h"
class HarmonyProofPanel : public QWidget {
    QNetworkAccessManager manager;
    QPointer<QNetworkReply> reply;
    QLineEdit *url;
    QLabel *status;
    QTreeWidget *results;
    QPushButton *stop;
    QPointer<HarmonyFloatingPanel> floating;
    QString source, path, settingsPath;
    int position=0, firstLine=0, count=0;
    bool cancelled=false, busy=false;
    quint64 generation=0;
    void next() {
        if(cancelled) return;
        if(position>=source.size()) {busy=false;status->setText(QStringLiteral("完成：%1 条建议。").arg(count));stop->setEnabled(false);return;}
        int n=qMin(6000,source.size()-position);
        if(position+n<source.size()) {int cut=source.lastIndexOf('\n',position+n-1);if(cut>position+1000)n=cut-position+1;}
        int base=position;QString text=harmonyProofreadText(source.mid(base,n));position+=n;
        QUrl endpoint(url->text().trimmed());if(!endpoint.path().endsWith("/v2/check"))endpoint.setPath(endpoint.path().replace(QRegularExpression("/$"),"")+"/v2/check");
        if(!harmonyValidServiceUrl(endpoint)){busy=false;status->setText(QStringLiteral("服务地址无效"));stop->setEnabled(false);return;}
        QSettings(settingsPath,QSettings::IniFormat).setValue("serviceUrl",endpoint.toString());
        harmonyInitializeTls();QUrlQuery form;form.addQueryItem("language","zh-CN");form.addQueryItem("text",text);
        QNetworkRequest req(endpoint);req.setHeader(QNetworkRequest::ContentTypeHeader,"application/x-www-form-urlencoded");
        reply=manager.post(req,form.query(QUrl::FullyEncoded).replace("+","%2B").toUtf8());auto *active=reply.data();
        status->setText(QStringLiteral("正在校对 %1 / %2 字符…").arg(position).arg(source.size()));stop->setEnabled(true);
        QTimer::singleShot(30000,active,[active]{if(active->isRunning())active->abort();});
        const auto task=generation;
        connect(active,&QNetworkReply::finished,this,[=]{
            active->deleteLater();if(task!=generation)return;
            reply=nullptr;
            if(cancelled){status->setText(QStringLiteral("已取消；已有结果保留"));stop->setEnabled(false);return;}
            if(active->error()!=QNetworkReply::NoError){busy=false;status->setText(QStringLiteral("校对未完成：")+active->errorString());stop->setEnabled(false);return;}
            auto obj=QJsonDocument::fromJson(active->readAll()).object();if(!obj["matches"].isArray()){busy=false;status->setText(QStringLiteral("服务结果无效"));stop->setEnabled(false);return;}
            for(auto value:obj["matches"].toArray()) {
                auto m=value.toObject();int offset=m["offset"].toInt(-1),length=m["length"].toInt();if(offset<0 || offset+length>text.size())continue;
                int line=firstLine+source.left(base+offset).count('\n');QStringList suggestions;
                for(auto replacement:m["replacements"].toArray()) suggestions<<replacement.toObject()["value"].toString();
                auto *item=new QTreeWidgetItem(results,{QFileInfo(path).fileName(),QString::number(line+1),source.mid(base+offset,length),m["message"].toString(),suggestions.mid(0,5).join(" / ")});
                item->setData(0,Qt::UserRole,path);item->setData(1,Qt::UserRole,line);++count;
            }
            QTimer::singleShot(250,this,[this,task]{if(task==generation)next();});
        });
    }
public:
    std::function<void(QString,int)> jump;
    explicit HarmonyProofPanel(QString settings,QWidget *parent=nullptr):QWidget(parent),manager(this),settingsPath(settings) {
        auto *layout=new QVBoxLayout(this);auto *bar=new QHBoxLayout;
        url=new QLineEdit(QSettings(settings,QSettings::IniFormat).value("serviceUrl","https://api.languagetool.org/v2/check").toString(),this);
        url->setToolTip(QStringLiteral("在线服务：只发送当前文件全文或选区，屏蔽常见公式/命令。可替换为自建 LanguageTool 服务。"));bar->addWidget(url,1);
        stop=new QPushButton(QStringLiteral("停止"),this);stop->setEnabled(false);bar->addWidget(stop);auto *expand=new QToolButton(this);expand->setText(QStringLiteral("⛶"));expand->setToolTip(QStringLiteral("展开覆盖编辑与 PDF 区 / 还原"));bar->addWidget(expand);layout->addLayout(bar);
        connect(expand,&QToolButton::clicked,this,[this]{if(floating)floating->close();else floating=new HarmonyFloatingPanel(this,QStringLiteral("中文校对"),false);});
        status=new QLabel(QStringLiteral("左侧“中文校对”入口：有选区时校对选区，否则校对当前文件全文。"),this);status->setWordWrap(true);layout->addWidget(status);
        results=new QTreeWidget(this);results->setColumnCount(5);results->setHeaderLabels({QStringLiteral("文件"),QStringLiteral("行"),QStringLiteral("原文"),QStringLiteral("问题"),QStringLiteral("建议")});results->setRootIsDecorated(false);results->header()->setSectionResizeMode(QHeaderView::ResizeToContents);results->header()->setStretchLastSection(true);layout->addWidget(results,1);
        connect(stop,&QPushButton::clicked,this,[this]{++generation;cancelled=true;busy=false;auto old=reply;reply=nullptr;if(old)old->abort();status->setText(QStringLiteral("已取消；已有结果保留"));stop->setEnabled(false);});
        connect(results,&QTreeWidget::itemDoubleClicked,this,[this](QTreeWidgetItem *item,int){if(jump)jump(item->data(0,Qt::UserRole).toString(),item->data(1,Qt::UserRole).toInt());});
    }
    void start(QString text,QString file,int line) {
        if(busy){status->setText(QStringLiteral("请先停止当前校对"));return;}
        ++generation;cancelled=false;source=text;path=file;firstLine=line;position=0;count=0;results->clear();
        if(source.size()>600000){status->setText(QStringLiteral("超过 60 万字符，请分选区校对。"));return;}
        busy=true;next();
    }
};
#endif

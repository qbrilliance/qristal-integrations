import * as React from 'react';
import parse from 'html-react-parser';
import { injectable, postConstruct, inject } from '@theia/core/shared/inversify';
import { AlertMessage } from '@theia/core/lib/browser/widgets/alert-message';
import { ReactWidget } from '@theia/core/lib/browser/widgets/react-widget';
import { MessageService } from '@theia/core';
import { Message } from '@theia/core/lib/browser';
import { URI } from '@theia/core/lib/common/uri';
import { MarkdownPreviewHandler } from './markdown/markdown-preview-handler';
// const link = new URI('file:/mnt/qb/html/index.html');
const previewHandler = new MarkdownPreviewHandler();
(previewHandler as any).linkNormalizer = {
        normalizeLink: (documentUri: URI, link: string) =>
            documentUri.parent.parent.resolve(link).path.toString().substr(1)
    };
// const reader = new FileReader();
// reader.readAsText('./221116-test.md');
// const useDidMount = require("!!raw-loader!./221116-test");

import textmd from './221116-test';

// const exmd = //
// `# Theia - Preview Extension
// Shows a preview of supported resources.
// See [here](https://github.com/eclipse-theia/theia).
// ## License
// [ Apache-2.0](https://github.com/eclipse-theia/theia/blob/master/LICENSE)
// `;

const contentElement = previewHandler.renderContent({ content: textmd, originUri: new URI('file:///workspace/DEMO.md') });

@injectable()
export class W22wWidget extends ReactWidget {

    static readonly ID = 'w22w:widget';
    static readonly LABEL = 'SDK';


    @inject(MessageService)
    protected readonly messageService!: MessageService;

    @postConstruct()
    protected async init(): Promise < void> {
        this.id = W22wWidget.ID;
        this.title.label = W22wWidget.LABEL;
        this.title.caption = W22wWidget.LABEL;
        this.title.closable = true;
        this.title.iconClass = 'fa fa-window-maximize'; // example widget icon.
        this.update();
    }

    render(): React.ReactElement {
        const header = `Beta release - SDK Documentation - v1`;
        return <div id='widget-container'>
            <AlertMessage type='INFO' header={header} />
            <div> { parse(contentElement.innerHTML) } </div>
            <button id='displayMessageButton' className='theia-button secondary' title='Contributors' onClick={_a => this.displayMessage()}>List of Contributors</button>
        </div>
    }

    protected displayMessage(): void {
        this.messageService.info('Quantum Brilliance Software and Applications Team 2022');
    }

    protected onActivateRequest(msg: Message): void {
        super.onActivateRequest(msg);
        const htmlElement = document.getElementById('displayMessageButton');
        if (htmlElement) {
            htmlElement.focus();
        }
    }

}

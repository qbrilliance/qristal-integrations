import { ContainerModule } from '@theia/core/shared/inversify';
import { W22wWidget } from './w22w-widget';
import { W22wContribution } from './w22w-contribution';
import { bindViewContribution, FrontendApplicationContribution, WidgetFactory } from '@theia/core/lib/browser';

import '../../src/browser/style/index.css';

export default new ContainerModule(bind => {
    bindViewContribution(bind, W22wContribution);
    bind(FrontendApplicationContribution).toService(W22wContribution);
    bind(W22wWidget).toSelf();
    bind(WidgetFactory).toDynamicValue(ctx => ({
        id: W22wWidget.ID,
        createWidget: () => ctx.container.get<W22wWidget>(W22wWidget)
    })).inSingletonScope();
});

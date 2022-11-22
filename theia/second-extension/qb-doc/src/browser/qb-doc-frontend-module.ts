/**
 * Generated using theia-extension-generator
 */
import { QbDocCommandContribution, QbDocMenuContribution } from './qb-doc-contribution';
import {
    CommandContribution,
    MenuContribution
} from "@theia/core/lib/common";
import { ContainerModule } from "inversify";

export default new ContainerModule(bind => {
    // add your contribution bindings here
    bind(CommandContribution).to(QbDocCommandContribution);
    bind(MenuContribution).to(QbDocMenuContribution);
});

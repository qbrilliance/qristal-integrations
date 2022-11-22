import { injectable, inject } from '@theia/core/shared/inversify';
import { MenuModelRegistry } from '@theia/core';
import { W22wWidget } from './w22w-widget';
import { AbstractViewContribution, FrontendApplicationContribution, FrontendApplication } from '@theia/core/lib/browser';
import { FrontendApplicationStateService } from '@theia/core/lib/browser/frontend-application-state';
import { Command, CommandRegistry } from '@theia/core/lib/common/command';

export const W22wCommand: Command = { id: 'w22w:command' };

@injectable()
export class W22wContribution extends AbstractViewContribution<W22wWidget>
       implements FrontendApplicationContribution {

    /**
     * `AbstractViewContribution` handles the creation and registering
     *  of the widget including commands, menus, and keybindings.
     * 
     * We can pass `defaultWidgetOptions` which define widget properties such as 
     * its location `area` (`main`, `left`, `right`, `bottom`), `mode`, and `ref`.
     * 
     */
    constructor() {
        super({
            widgetId: W22wWidget.ID,
            widgetName: W22wWidget.LABEL,
            defaultWidgetOptions: { area: 'left' },
            toggleCommandId: W22wCommand.id
        });
    }

    /**
     * Example command registration to open the widget from the menu, and quick-open.
     * For a simpler use case, it is possible to simply call:
     ```ts
        super.registerCommands(commands)
     ```
     *
     * For more flexibility, we can pass `OpenViewArguments` which define 
     * options on how to handle opening the widget:
     * 
     ```ts
        toggle?: boolean
        activate?: boolean;
        reveal?: boolean;
     ```
     *
     * @param commands
     */
    registerCommands(commands: CommandRegistry): void {
        commands.registerCommand(W22wCommand, {
            execute: () => super.openView({ activate: true, reveal: true })
        });
    }

    /**
     * Example menu registration to contribute a menu item used to open the widget.
     * Default location when extending the `AbstractViewContribution` is the `View` main-menu item.
     * 
     * We can however define new menu path locations in the following way:
     ```ts
        menus.registerMenuAction(CommonMenus.HELP, {
            commandId: 'id',
            label: 'label'
        });
     ```
     * 
     * @param menus
     */
    registerMenus(menus: MenuModelRegistry): void {
        super.registerMenus(menus);
    }

    @inject(FrontendApplicationStateService)
    protected readonly stateService: FrontendApplicationStateService;
    async onStart(app: FrontendApplication): Promise<void> {
        this.stateService.reachedState('ready').then(
               () => this.openView({ reveal: true })
            );
        }

}

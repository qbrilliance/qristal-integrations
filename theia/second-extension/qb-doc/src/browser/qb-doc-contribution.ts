import { injectable, inject } from 'inversify';
import { CommandContribution, CommandRegistry, MenuContribution, MenuModelRegistry } from '@theia/core/lib/common';
import { CommonMenus } from '@theia/core/lib/browser';
import { MiniBrowserOpenHandler } from '@theia/mini-browser/lib/browser/mini-browser-open-handler';
import URI from '@theia/core/lib/common/uri';

export const QbDocCommand = {
	id: 'qb.command',
	label: 'Documentation'
};

const link = new URI('file:/mnt/qb/html/index.html');

@injectable()
export class QbDocCommandContribution implements CommandContribution {
	constructor(@inject(MiniBrowserOpenHandler) private readonly miniBrowserOpenHandler: MiniBrowserOpenHandler) {}

	registerCommands(registry: CommandRegistry): void {
		registry.registerCommand(QbDocCommand, {
			execute: () => {
				this.miniBrowserOpenHandler.open(link);
			}
		});
	}
}

@injectable()
export class QbDocMenuContribution implements MenuContribution {
	registerMenus(menus: MenuModelRegistry): void {
		menus.registerMenuAction(CommonMenus.HELP, {
			commandId: QbDocCommand.id,
			label: QbDocCommand.label
		});
	}
}

import { mainButton } from '@tma.js/sdk-react';
import { useEffect } from 'react';

interface MainButtonParams {
  text?: string;
  isVisible?: boolean;
  isEnabled?: boolean;
  onClick?: () => void | Promise<void>;
}

/**
 * Hook for mounting and configuring main button of Telegram Mini App.
 */
export function useMainButton(
  {
    text,
    isVisible = false,
    isEnabled = true,
    onClick
  }: MainButtonParams)
{

  useEffect(() => {
    mainButton.mount();

    return () => {
      mainButton.unmount();
    };
  }, []);

  useEffect(() => {
    if (text) mainButton.setText(text);
  }, [text]);

  useEffect(() => {
    if (isVisible) {
      mainButton.show();
    } else {
      mainButton.hide();
    }
  }, [isVisible]);

  useEffect(() => {
    if (isEnabled) {
      mainButton.enable();
    } else {
      mainButton.disable();
    }
  }, [isEnabled]);

  useEffect(() => {
    if (!onClick) return;

    const handler = async () => {
      await onClick();
    };

    mainButton.onClick(handler);

    return () => {
      mainButton.offClick(handler);
    };
  }, [onClick]);
}

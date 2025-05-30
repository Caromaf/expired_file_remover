// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'expired-file-remover',
  tagline: '特定のディレクトリ内で作成・更新から一定期間を経過したファイルを削除するためのパッケージ',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://your-project-url.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/expired-file-remover/',

  // GitHub pages deployment config.
  organizationName: 'your-organization', // Usually your GitHub org/user name.
  projectName: 'expired-file-remover', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'ja',
    locales: ['ja'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/your-organization/expired-file-remover/tree/main/docs/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/social-card.jpg',
      navbar: {
        title: 'expired-file-remover',
        logo: {
          alt: 'expired-file-remover Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'ドキュメント',
          },
          {
            href: 'https://github.com/your-organization/expired-file-remover',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'ドキュメント',
            items: [
              {
                label: '使い方',
                to: '/docs/intro',
              },
            ],
          },
          {
            title: '開発者向け',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/your-organization/expired-file-remover',
              },
            ],
          },
          {
            title: 'その他',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/your-organization/expired-file-remover',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} expired-file-remover プロジェクト. MIT License.`,
      },
      prism: {
        // 修正されたプリズムテーマ設定
        theme: {plain: {color: '#393A34',backgroundColor: '#f6f8fa'},styles: []},
        darkTheme: {plain: {color: '#F8F8F2',backgroundColor: '#282A36'},styles: []},
      },
    }),
};

module.exports = config;

import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: '簡単に使える',
    description: (
      <>
        expired-file-removerは直感的なAPIを提供し、わずか数行のコードで古いファイルを削除できます。
      </>
    ),
  },
  {
    title: '柔軟な期限指定',
    description: (
      <>
        日数、datetime、timedeltaなど、様々な方法で削除対象の期限を指定できます。
      </>
    ),
  },
  {
    title: '型ヒント完全対応',
    description: (
      <>
        すべての関数に型ヒントが付与されており、IDEの補完機能と型チェックが完全にサポートされています。
      </>
    ),
  },
];

function Feature({title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}

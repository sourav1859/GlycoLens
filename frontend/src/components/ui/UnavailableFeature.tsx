import Link from "next/link";
import { Icon } from "./Icon";
import { PageIntro } from "../layout/PageIntro";

export function UnavailableFeature({ title, description, icon = "chart" }: { title: string; description: string; icon?: string }) {
  return <><PageIntro title={title} description={description} /><section className="surface empty-panel"><span className="icon-tile large"><Icon name={icon} /></span><h2>This experience isn’t available yet</h2><p>You can explore the reviewed virtual-patient workflow while this page is being connected. No sample values are presented as your data.</p><Link className="button" href="/demo">Open virtual-patient demo<Icon name="arrow" /></Link></section></>;
}

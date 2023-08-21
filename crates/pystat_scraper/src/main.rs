use anyhow;
use tokio;
use serde_json;
use table_extract;


async fn list_pypi_pkgs() -> Result<(), anyhow::Error> {

    let body = reqwest::get("https://pypistats.org/top")
    .await?
    .text()
    .await?;

    println!("{:?}", &body[..100]);

    let table = table_extract::Table::find_first(&body).unwrap();
    for row in &table {
        println!(
            "{:?}",
            row.get(None)
        )
    }

    Ok(())

}


#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    let foo = list_pypi_pkgs().await?;
    println!("{:?}", foo);
    Ok(())
}

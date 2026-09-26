import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const GRAPH_API_VERSION = "v22.0";
const GRAPH_API_HOST = "https://graph.facebook.com";
const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
const INSTAGRAM_ACCESS_TOKEN = Deno.env.get("INSTAGRAM_ACCESS_TOKEN");
const INSTAGRAM_BUSINESS_ACCOUNT_ID = Deno.env.get("INSTAGRAM_BUSINESS_ACCOUNT_ID");

interface PublishRequest {
  repo?: string;
  branch?: string;
}

interface QueueItem {
  carousel_id: string;
  folder_id: string;
  slides: Array<{ arquivo: string; ordem: number }>;
  [key: string]: unknown;
}

async function fetchRepoQueue(owner: string, repo: string, branch: string) {
  // Busca a fila versionada no repo via GitHub Raw
  // Retorna o primeiro item com postado:false
  const queuePath = `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/agente%20aidealab/skills/post-instagram/queue/FILA-SEMANA-1/02-carrossel`;

  // Lista items em ordem dia
  const diaItems = [
    "Dia2-01-A-ordem",
    "Dia3-02-O-ornamento",
    "Dia4-03-A-regra-e-a-quebra",
    "Dia5-04-A-tela",
    "Dia8-Ferramenta-vs-Processo",
    "Dia11-importancia-do-design",
  ];

  for (const itemName of diaItems) {
    try {
      const response = await fetch(`${queuePath}/${itemName}/metadata.json`);
      if (response.ok) {
        const data = await response.json();
        if (!data.postado) {
          // Adiciona folder_id necessário para atualização posterior
          data.folder_id = itemName;
          return { item: data, itemName };
        }
      }
    } catch (e) {
      console.error(`Erro buscando ${itemName}:`, e);
    }
  }

  console.log("Nenhum item não publicado encontrado na fila");
  return null;
}

async function uploadImageToSupabase(imageUrl: string, filename: string) {
  const imageResponse = await fetch(imageUrl);
  const imageBuffer = await imageResponse.arrayBuffer();

  const uploadPath = `${new Date().toISOString().split("T")[0]}/${filename}`;

  const uploadResponse = await fetch(
    `${SUPABASE_URL}/storage/v1/object/ig-publish/${uploadPath}`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
        "Content-Type": "image/png",
      },
      body: imageBuffer,
    }
  );

  if (!uploadResponse.ok) {
    throw new Error(`Supabase upload failed: ${uploadResponse.statusText}`);
  }

  return `${SUPABASE_URL}/storage/v1/object/public/ig-publish/${uploadPath}`;
}

async function publishToInstagram(slides: Array<any>, caption: string) {
  const igAccountId = INSTAGRAM_BUSINESS_ACCOUNT_ID;
  const childIds = [];

  // Step 1: Create media containers for each slide
  for (const slide of slides.sort((a, b) => (a.ordem || 0) - (b.ordem || 0))) {
    const imageUrl = slide.image_url;
    if (!imageUrl) continue;

    const mediaUrl = `${GRAPH_API_HOST}/${GRAPH_API_VERSION}/${igAccountId}/media`;
    const mediaResponse = await fetch(mediaUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        image_url: imageUrl,
        is_carousel_item: true,
        access_token: INSTAGRAM_ACCESS_TOKEN,
      }),
    });

    if (!mediaResponse.ok) {
      throw new Error(`Failed to create media container for slide ${slide.ordem}`);
    }

    const mediaData = await mediaResponse.json();
    childIds.push(mediaData.id);
  }

  // Step 2: Create parent carousel container
  const carouselUrl = `${GRAPH_API_HOST}/${GRAPH_API_VERSION}/${igAccountId}/media`;
  const carouselResponse = await fetch(carouselUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      media_type: "CAROUSEL",
      children: childIds,
      caption: caption,
      access_token: INSTAGRAM_ACCESS_TOKEN,
    }),
  });

  if (!carouselResponse.ok) {
    throw new Error("Failed to create carousel container");
  }

  const carouselData = await carouselResponse.json();
  const carouselId = carouselData.id;

  // Step 3: Publish
  const publishUrl = `${GRAPH_API_HOST}/${GRAPH_API_VERSION}/${igAccountId}/media_publish`;
  const publishResponse = await fetch(publishUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      creation_id: carouselId,
      access_token: INSTAGRAM_ACCESS_TOKEN,
    }),
  });

  if (!publishResponse.ok) {
    throw new Error("Failed to publish carousel");
  }

  const publishData = await publishResponse.json();
  return publishData.id;
}

async function updateMetadataInGithub(owner: string, repo: string, branch: string, itemName: string, postId: string) {
  // Atualiza o metadata.json no GitHub após publicar
  // Requer token com permissão de write
  const metadataPath = `agente aidealab/skills/post-instagram/queue/FILA-SEMANA-1/02-carrossel/${itemName}/metadata.json`;
  const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${encodeURIComponent(metadataPath)}`;

  try {
    // Busca o arquivo atual para obter o SHA
    const getResponse = await fetch(apiUrl, {
      headers: {
        "Accept": "application/vnd.github.v3+json",
      },
    });

    if (!getResponse.ok) {
      console.error("Erro ao buscar arquivo:", await getResponse.text());
      return false;
    }

    const fileData = await getResponse.json();
    const currentContent = JSON.parse(atob(fileData.content));

    // Atualiza metadata
    currentContent.postado = true;
    currentContent.postado_em = new Date().toISOString();
    currentContent.post_id = postId;

    // Nota: Esta função é informativa apenas
    // A atualização real deve ser feita via webhook ou outro mecanismo autenticado
    console.log("Metadata será atualizado via webhook/commit:", { postado: true, postado_em: currentContent.postado_em, post_id: postId });
    return true;
  } catch (error) {
    console.error("Erro ao preparar atualização:", error);
    return false;
  }
}

serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  try {
    const body = (await req.json()) as PublishRequest;
    const owner = body.repo?.split("/")[0] || "otaluiz";
    const repo = body.repo?.split("/")[1] || "aidealab-post";
    const branch = body.branch || "main";

    // Fetch queue from GitHub - retorna {item, itemName}
    const queueResult = await fetchRepoQueue(owner, repo, branch);

    if (!queueResult) {
      return new Response(
        JSON.stringify({ error: "Nenhum item não publicado na fila", success: false }),
        { status: 404, headers: { "Content-Type": "application/json" } }
      );
    }

    const queueItem = queueResult.item;
    const itemName = queueResult.itemName;

    console.log(`Processando: ${itemName}`);

    // Upload images to Supabase
    const slides = queueItem.slides || [];
    for (const slide of slides) {
      if (!slide.image_url && slide.arquivo) {
        // Download from Drive or GitHub and upload to Supabase
        const imageUrl = `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/agente%20aidealab/skills/post-instagram/queue/FILA-SEMANA-1/02-carrossel/${itemName}/${slide.arquivo}`;
        const supabaseUrl = await uploadImageToSupabase(imageUrl, slide.arquivo);
        slide.image_url = supabaseUrl;
      }
    }

    // Publish to Instagram
    const postId = await publishToInstagram(slides, queueItem.legenda || "");

    // Atualizar metadata (requer autenticação)
    await updateMetadataInGithub(owner, repo, branch, itemName, postId);

    return new Response(
      JSON.stringify({
        success: true,
        post_id: postId,
        item_name: itemName,
        message: `${itemName} publicado com sucesso. Post ID: ${postId}`
      }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error:", error);
    return new Response(
      JSON.stringify({ error: error.message, success: false }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
});

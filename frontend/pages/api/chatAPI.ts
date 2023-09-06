import { ChatBody } from '@/types/types';
import { OpenAIStream, getBackendResponse } from '@/utils/chatStream';

export const config = {
  runtime: 'edge',
};

const handler = async (req: Request): Promise<Response> => {
  try {
    /* const { inputCode, model, apiKey } = (await req.json()) as ChatBody;
    let apiKeyFinal;

    if (apiKey) {
      apiKeyFinal = apiKey;
    } else {
      apiKeyFinal = process.env.NEXT_PUBLIC_OPENAI_API_KEY;
    }

    if (!apiKey) {
      return new Response('API key not found', { status: 500 });
    } */

    const question = 'Your Question here'; // Get the user's question here
    const response = await getBackendResponse(question);
    console.log('Response from backend:', response);
    return new Response(response);

    /*     const stream = await OpenAIStream(inputCode, model, apiKeyFinal);

    return new Response(stream); */
  } catch (error) {
    console.error(error);
    return new Response('Error', { status: 500 });
  }
};

const handleChat = async () => {
  const question = 'Your Question here'; // Get the user's question here
  const response = await getBackendResponse(question);
  console.log('Response from backend:', response);
  return response;
};

export default handleChat;

"use client"

import { useState, useContext } from 'react';
import { useRouter } from 'next/navigation';
import Tiptap from './editor/Tiptap';
import { CreationPopupContext } from '../contexts/CreationPopupContext';

const BASE_API = process.env.NEXT_PUBLIC_BASE_API

export default function CommentCreator({entID, reloader, initialContent}) {
    const router = useRouter();
    const [content, setContent] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    // Onl;y use to set the text of the editor to nothing once the submit button is pressed.
    const [initial, setInitial] = useState(initialContent);
    const { user } = useContext(CreationPopupContext)

    const handleContentChange = (content) => {
        setContent(content);
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);

        const newComment = {
            content, 
        }

        let response = await fetch(BASE_API + "entities/" + entID + "?HTML=True" + "&username=" + user, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(newComment),
        });

        if (response.status === 201) {
            reloader();
            setContent("");
            setInitial("");
            setIsLoading(false);
        } else {
            alert ("Something went wrong, please try again.")
            setIsLoading(false)
        }
    }

    return (
        <div className="comment-creator">
            <h2>Add a comment</h2>
            <form onSubmit={handleSubmit}>
                <Tiptap onContentChange={handleContentChange}
                 entID={entID}
                 initialContent={initial}
                 />
                {isLoading && <p>Loading...</p>}
                {!isLoading && <button type="submit" className="submitButton">Submit</button>}
            </form>
        </div>
    )
}


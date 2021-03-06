import torch
import torch.nn.functional as F

from torch import nn


class MarginRankingLoss(nn.Module):
    def __init__(self, margin=1., aggregate=torch.mean):
        super(MarginRankingLoss, self).__init__()
        self.margin = margin
        self.aggregate = aggregate

    def forward(self, positive_similarity, negative_similarity):
        return self.aggregate(
            torch.clamp(self.margin - positive_similarity + negative_similarity, min=0))


class InnerProductSimilarity(nn.Module):
    def __init__(self):
        super(InnerProductSimilarity, self).__init__()

    def forward(self, a, b):
        # a => B x [n_a x] dim, b => B x [n_b x] dim

        if a.dim() == 2:
            a = a.unsqueeze(1)  # B x n_a x dim

        if b.dim() == 2:
            b = b.unsqueeze(1)  # B x n_b x dim

        return torch.bmm(a, b.transpose(2, 1))  # B x n_a x n_b


class StarSpace(nn.Module):
    def __init__(self, d_embed, n_input, n_output, similarity, max_norm=10, aggregate=torch.sum):
        super(StarSpace, self).__init__()

        self.n_input = n_input
        self.n_output = n_output
        self.similarity = similarity
        self.aggregate = aggregate
        
        self.input_embedding = nn.Embedding(n_input, d_embed, max_norm=max_norm)
        self.output_embedding = nn.Embedding(n_output, d_embed, max_norm=max_norm)

    def forward(self, input=None, output=None):
        input_repr, output_repr = None, None
        
        if input is not None:
            if input.dim() == 1:
                input = input.unsqueeze(-1)

            input_emb = self.input_embedding(input)  # B x L_i x dim
            input_repr = self.aggregate(input_emb, dim=1)  # B x dim
        
        if output is not None:
            if output.dim() == 1:
                output = output.unsqueeze(-1)  # B x L_o

            output_emb = self.output_embedding(output)  # B x L_o x dim
            output_repr = self.aggregate(output_emb, dim=1)  # B x dim
        
        return input_repr, output_repr
